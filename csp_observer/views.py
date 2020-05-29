import json
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
from .models import CspReport, Session
from .report_utils import raw_report_to_model

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
