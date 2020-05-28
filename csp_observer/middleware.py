import uuid
from django.urls import reverse
from . import settings as app_settings


class CspReportMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.csp_header_name = "Content-Security-Policy"
        if app_settings.REPORT_ONLY:
            self.csp_header_name = "Content-Security-Policy-Report-Only"
        
        self.csp_policies = app_settings.CSP_POLICIES

    def __call__(self, request):
        response = self.get_response(request)
        report_uri = reverse('report', args=(uuid.uuid4(), ))
        final_csp_policies = self.csp_policies + ["report-uri {}".format(report_uri)]

        response[self.csp_header_name] = "; ".join(final_csp_policies)


        return response