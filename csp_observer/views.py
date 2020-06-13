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
from .report_utils import raw_report_to_model
from . import settings as app_settings

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def report(request, session_id):
    report_str = request.body.decode('utf-8')
    report_data = json.loads(report_str)

    if not 'csp-report' in report_data:
        return HttpResponse('')

    csp_report_raw = report_data['csp-report']
    logger.info("Received CSP report")
    logger.info("Session ID: {}".format(session_id))
    logger.info("Report Data: {}".format(csp_report_raw))

    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return HttpResponse('')
    else:
        report = raw_report_to_model(csp_report_raw, session)
        report.save()
        logger.info("Report saved with id {}".format(report.id))
    
    return HttpResponse('')

@xframe_options_exempt
def result(request, session_id):
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

@staff_member_required
@never_cache
def admin(request):
    return render(request, 'admin/cspo_index.html')