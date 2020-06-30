import re
import logging
import json
from django.urls import reverse
from . import settings as app_settings
from .models import Session
from django.templatetags.static import static

class CspReportMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logger = logging.getLogger(__name__)

        self.reporting_group_name = "csp-observer"
        self.csp_header_name = "Content-Security-Policy"
        if app_settings.REPORT_ONLY:
            self.csp_header_name = "Content-Security-Policy-Report-Only"
        
        self.csp_policies = app_settings.CSP_POLICIES
        # compile regexes for all enabled paths
        self.paths_regex = [re.compile("^{}$".format(p)) for p in app_settings.ENABLED_PATHS]

    def anonymize_ip(self, ip_address):
        """Removes the last two octets from the ip_address"""
        return ".".join(ip_address.split(".")[:2] + 2*["0"])

    def create_session(self, request):
        """Creates a new session object, stores it in the database and returns the session id"""
        session = Session(
            user_agent=request.META["HTTP_USER_AGENT"],
            anonymized_ip=self.anonymize_ip(request.META["REMOTE_ADDR"])
        )
        session.save()
        self.logger.debug("session created: {}".format(session.id))
        return session.id

    def add_csp_header(self, request, response, session_id):
        """Adds a CSP header to the response, returns the response"""
        report_uri = request.build_absolute_uri(reverse('report', args=(session_id, )))
        # set fallback reporting directive
        reporting_directives = [
            "report-uri {}".format(report_uri),
        ]
        # New Reporting API stuff (not working?!):
        # https://w3c.github.io/reporting/
        #response["Reporting-Endpoints"] = '{}="{}"'.format(self.reporting_group_name, report_uri)
        report_to_group_definition = {
            "group": self.reporting_group_name,
            "max_age": 86400,
            "include_subdomains": True,
            "endpoints": [{
                "url": report_uri,
            }]
        }
        if app_settings.ENABLE_NEW_API:
            reporting_directives.append("report-to {}".format(self.reporting_group_name))
            response["Report-To"] = json.dumps(report_to_group_definition)

        # build final csp policy directive string
        final_csp_policies = self.csp_policies + reporting_directives
        response[self.csp_header_name] = "; ".join(final_csp_policies)

        return response

    def add_tripwire(self, request, response, session_id):
        tripwire_js_path = static('js/tripwire.js')
        tripwire_js_uri = request.build_absolute_uri(tripwire_js_path)
        script_tag_string = '<script type="text/javascript" data-session="{}" src="{}"></script>'.format(session_id, tripwire_js_uri)
        response.content = response.content.replace(b'</body>', str.encode(script_tag_string + '</body>'))
        return response

    def __call__(self, request):
        # check if path in enabled paths
        for path_regex in self.paths_regex:
            if path_regex.match(request.path):
                self.logger.debug("match for path {}".format(request.path))
                session_id = self.create_session(request)
                request.cspo_session_id = session_id
                response = self.get_response(request)
                response = self.add_csp_header(request, response, session_id)
                response = self.add_tripwire(request, response, session_id)
                return response
        
        return self.get_response(request)