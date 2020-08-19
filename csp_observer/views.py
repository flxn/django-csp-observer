import json
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
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
from django.core.paginator import Paginator
from django.views.generic import ListView
from django import forms

logger = logging.getLogger(__name__)

@csrf_exempt
def report(request, report_type, session_id):
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
    serialized = serializers.serialize('json', reports)
    return HttpResponse(serialized)

def result_detail(request, session_id):
    if app_settings.REMOTE_REPORTING:
        # don't do anything if remote reporting is enabled
        return HttpResponse('')

    session = get_object_or_404(Session, pk=session_id)
    
    reports = session.cspreport_set.all()
    return render(request, 'client_ui/result_detail.html', {'reports': reports })

@require_POST
@csrf_exempt
def master_session(request, session_id):
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
        fields = ['title', 'blocked_url', 'description', 'effective_directive']

@staff_member_required
@never_cache
@csrf_exempt
def admin(request):
    cspreports = CspReport.objects.all()
    paginator1 = Paginator(cspreports, 2)

    csprules = CspRule.objects.all() # This should be changed to rules, but I have reports for testing purposes
    paginator2 = Paginator(csprules, 3)

    page_number1 = request.GET.get('page')
    page_obj1 = paginator1.get_page(page_number1)

    page_number2 = request.GET.get('page2')
    page_obj2 = paginator2.get_page(page_number2)

    if request.method == 'POST':
        form = CspRuleForm(request.POST)
        if form.is_valid():
            form.save(commit=True)

            return render(request, 'admin/cspo_index.html', {'cspreports': page_obj1, 'csprules':page_obj2})
    return render(request, 'admin/cspo_index.html', {'cspreports': page_obj1, 'csprules':page_obj2})

def privacy(request):
    return render(request, 'client_ui/privacy.html')
