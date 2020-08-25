import json
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.views import generic
from django.core import serializers
from .models import CspReport, Session, CspRule
from .report_handlers import handle_csp_report, handle_tripwire_report, REPORT_TYPE_CSP, REPORT_TYPE_TRIPWIRE
from . import settings as app_settings
from .update import update_rules
from .remote import share_session_data
from django.core.paginator import Paginator
from django.views.generic import ListView
from django import forms
from django.forms.models import model_to_dict
from django.db.models import Count
import markdown as md

logger = logging.getLogger(__name__)

@csrf_exempt
def report(request, report_type, session_id):
    """Handles CSP report-uri requests."""
    if app_settings.REMOTE_REPORTING or request.method != 'POST':
        # don't do anything if remote reporting is enabled
        return HttpResponse('')

    report_str = request.body.decode('utf-8')
    report_data = json.loads(report_str)

    if report_type == REPORT_TYPE_CSP:
        handle_csp_report(report_data, session_id)
    elif report_type == REPORT_TYPE_TRIPWIRE:
        handle_tripwire_report(report_data, session_id)

    return HttpResponse('')

def result(request, session_id):
    """Handles result requests from the clientui component."""
    if app_settings.REMOTE_REPORTING:
        # don't do anything if remote reporting is enabled
        return HttpResponse('')

    session = get_object_or_404(Session, pk=session_id)
    
    # check session creation date and wait at least RESULT_WAIT_TIME seconds before returning
    current_time = timezone.now()
    min_return_time = session.created_at + timedelta(seconds=app_settings.RESULT_WAIT_TIME)
    if current_time <= min_return_time:
        time.sleep((min_return_time - current_time).seconds) 

    reports = session.cspreport_set.all()
    rules = {}
    for report in reports:
        for rule in report.matching_rules.get_global():
            if not rule.global_id in rules:
                rules[rule.global_id] = model_to_dict(rule)
        for rule in report.matching_rules.get_custom():
            if not rule.id in rules:
                rules[rule.id] = model_to_dict(rule)
    
    return JsonResponse(list(rules.values()), safe=False)

def result_detail(request, session_id):
    """Handles the request to the scan report page where the user can view their session reports."""
    if app_settings.REMOTE_REPORTING:
        # don't do anything if remote reporting is enabled
        return HttpResponse('')

    session = get_object_or_404(Session, pk=session_id)
    reports = session.cspreport_set.all()
    rules = {}
    for report in reports:
        for rule in report.matching_rules.get_global():
            if not rule.global_id in rules:
                rules[rule.global_id] = rule
        for rule in report.matching_rules.get_custom():
            if not rule.id in rules:
                rules[rule.id] = rule
    reports_without_match = [model_to_dict(x) for x in reports.filter(matching_rules=None)]

    shared_data = {
        'session': model_to_dict(session),
        'unknown_reports': reports_without_match
    }

    # prerender markdown here so we don't need a custom templatetag
    for k in rules.keys():
        rules[k].long_description = md.markdown(rules[k].long_description, extensions=['markdown.extensions.fenced_code'])

    return render(request, 'client_ui/result_detail.html', {
        'rules': rules, 
        'other_reports': reports_without_match,
        'session': session,
        'shared_data': shared_data
    })

@require_POST
@csrf_exempt
def master_session(request, session_id):
    """Handles the remote creation of a new session if instance is master collector."""
    if not app_settings.IS_MASTER_COLLECTOR:
        return HttpResponse('')
    if not app_settings.REMOTE_SECRET or len(app_settings.REMOTE_SECRET) == 0:
        return HttpResponse('')
    if not app_settings.REMOTE_SECRET == request.POST['secret']:
        return HttpResponse('')

    user_agent = request.POST['user_agent']
    anonymized_ip = request.POST['anonymized_ip']
    session = Session(
        id=session_id,
        user_agent=user_agent,
        anonymized_ip=anonymized_ip
    )
    session.save()
    logger.debug("created session {}".format(session.id))
    return session.id

    return HttpResponse('')


class CspRuleForm(forms.ModelForm):
    class Meta:
        model = CspRule
        fields = ['title', 'blocked_url', 'short_description', 'effective_directive']

@staff_member_required
@never_cache
@csrf_exempt
def admin(request):
    """Handles access of the admin dashboard."""
    cspreports = CspReport.objects.all().order_by('-created_at')
    paginator1 = Paginator(cspreports, 5)

    csprules = CspRule.objects.get_custom().order_by('title')
    paginator2 = Paginator(csprules, 5)
    
    global_database_rules = CspRule.objects.get_global().values('global_id', 'title', 'short_description').distinct().order_by('title')
    global_rules_paginator = Paginator(global_database_rules, 5)

    page_number1 = request.GET.get('page')
    page_obj1 = paginator1.get_page(page_number1)

    page_number2 = request.GET.get('page2')
    page_obj2 = paginator2.get_page(page_number2)

    global_rules_page = request.GET.get('global_rules_page')
    global_rules_page_obj = global_rules_paginator.get_page(global_rules_page)

    settings_keys = [item for item in dir(app_settings) if (not item.startswith("__") and item.isupper())]
    settings_list = [(key, getattr(app_settings, key)) for key in settings_keys]

    last_rule_update = app_settings.get_stored(app_settings.KEY_LAST_RULE_UPDATE, default=None)
    last_rule_update = datetime.fromtimestamp(float(last_rule_update if last_rule_update else 0))

    if request.method == 'POST':
        form = CspRuleForm(request.POST)
        if form.is_valid():
            form.save(commit=True)

    return render(request, 'admin/dashboard.html', {
        'cspreports': page_obj1, 
        'csprules': page_obj2, 
        'settings': settings_list,
        'global_rules': {
            'pagination': global_rules_page_obj,
            'count': global_database_rules.count(),
            'last_updated': last_rule_update
        },
    })

@require_POST
def admin_update_rules(request):
    """Handles the manual global rule update request from the admin dashboard."""
    try:
        count_pre, new_rules, count_post = update_rules(force=True)
        return JsonResponse({
            'status': 'ok',
            'message': 'Database Updated Successfully.',
            'count_pre': count_pre,
            'new_rules': new_rules,
            'count_post': count_post
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@require_POST
def delete_custom_rule(request, rule_id):
    """Handles the custom rule deletion request from the admin dashboard."""
    try:
        num_deleted, _ = CspRule.objects.get(id=rule_id).delete()
        return JsonResponse({
            'status': 'ok',
            'message': 'Rule {} has been removed from the database.'.format(rule_id)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@require_POST
def share_session(request, session_id):
    """Handles the user's voluntary data sharing request from the result detail (scan report) page."""
    session = get_object_or_404(Session, pk=session_id)
    reports_without_match = [model_to_dict(x) for x in session.cspreport_set.filter(matching_rules=None)]

    shared_data = {
        'session': model_to_dict(session),
        'unknown_reports': reports_without_match
    }

    try:
        status, response = share_session_data(session_id, shared_data)
        if status >= 200 and status < 300:
            return JsonResponse({
                'status': 'ok',
                'message': 'The data has been submitted. Thank you!'
            })
    except Exception as e:
        print(e)
        pass

    return JsonResponse({
        'status': 'error',
        'message': 'There was an error communicating with the sharing service.'
    })

def privacy(request):
    return render(request, 'client_ui/privacy.html')

#
# Charts
#

def chart_observed_rule_distribution(request):
    """Returns the JSON data for the observed rule distribution chart on the admin dashboard."""
    counts = {}
    first_relevant_date = timezone.now() - timedelta(days=14)
    reports = CspReport.objects.filter(created_at__gt=first_relevant_date)

    for report in reports:
        raw_data = report.matching_rules.values('global_id', 'title').annotate(observed_count=Count('id'))
        for val in raw_data:
            label = "{} ({})".format(val['title'], val['global_id'])
            if not label in counts:
                counts[label] = 0
            counts[label] += val['observed_count']
    
    chart_data = {
        'labels': [x for x in counts.keys()],
        'datasets': [{
            'data': [x for x in counts.values()],
        }]
    }

    return JsonResponse(chart_data)

def chart_reports_per_day(request):
    """Returns the JSON data for the reports per day chart on the admin dashboard."""
    counts = {}
    first_relevant_date = timezone.now() - timedelta(days=14)
    reports = CspReport.objects.filter(created_at__gt=first_relevant_date).extra(select={'day': 'date( created_at )'}).values('day') \
               .annotate(count=Count('created_at'))

    chart_data = {
        'labels': [x['day'] for x in reports],
        'datasets': [{
            'label': 'Reports Per Day',
            'data': [x['count'] for x in reports],
        }]
    }

    return JsonResponse(chart_data)