import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint

@require_POST
@csrf_exempt
def report(request, report_id):
    report_str = request.body.decode('utf-8')
    report_data = json.loads(report_str)

    if 'csp-report' in report_data:
        print("\n----- CSP Report -----")
        print("Report ID: {}".format(report_id))
        pprint(report_data['csp-report'])
        print("----------------------\n")

    return HttpResponse('')