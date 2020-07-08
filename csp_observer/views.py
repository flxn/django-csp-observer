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
from pprint import pprint
from .models import CspReport, Session
from .report_handlers import handle_csp_report, handle_tripwire_report, REPORT_TYPE_CSP, REPORT_TYPE_TRIPWIRE
from . import settings as app_settings

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def report(request, report_type, session_id):
    if app_settings.REMOTE_REPORTING:
        # don't do anything if remote reporting is enabled
        return HttpResponse('')

    report_str = request.body.decode('utf-8')
    report_data = json.loads(report_str)

    if report_type == REPORT_TYPE_CSP:
        handle_csp_report(report_data, session_id)
    elif report_type == REPORT_TYPE_TRIPWIRE:
        handle_tripwire_report(report_data, session_id)

    return HttpResponse('')

@xframe_options_exempt
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
    return render(request, 'inline_result.html', {
        'reports': reports
    })

@require_POST
@csrf_exempt
def master_session(request):
    if not app_settings.IS_MASTER_COLLECTOR:
        return HttpResponse('')
    
    return HttpResponse(request)

@staff_member_required
@never_cache
def admin(request):
    return render(request, 'admin/cspo_index.html')