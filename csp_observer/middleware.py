import uuid
import re
import logging
from django.urls import reverse
from . import settings as app_settings

class CspReportMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logger = logging.getLogger(__name__)

        self.csp_header_name = "Content-Security-Policy"
        if app_settings.REPORT_ONLY:
            self.csp_header_name = "Content-Security-Policy-Report-Only"
        
        self.csp_policies = app_settings.CSP_POLICIES
        self.paths_regex = [re.compile("^{}$".format(p)) for p in app_settings.ENABLED_PATHS]

    def add_csp_header(self, response):
        report_uri = reverse('report', args=(uuid.uuid4(), ))
        final_csp_policies = self.csp_policies + ["report-uri {}".format(report_uri)]

        response[self.csp_header_name] = "; ".join(final_csp_policies)
        return response

    def __call__(self, request):
        response = self.get_response(request)
        for path_regex in self.paths_regex:
            if path_regex.match(request.path):
                self.logger.debug("Match for path {}".format(request.path))
                return self.add_csp_header(response)
        
        self.logger.debug("{} is not a matching path".format(request.path))
        return response