import json
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def report(request, report_id):
    report_str = request.body.decode('utf-8')
    report_data = json.loads(report_str)

    if 'csp-report' in report_data:
        logger.info("Received CSP report")
        logger.info("Report ID: {}".format(report_id))
        logger.info("Report Data: {}".format(report_data['csp-report']))

    return HttpResponse('')