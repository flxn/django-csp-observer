import re
import logging
import json
import base64
import uuid
import asyncio
import random
from django.urls import reverse
from . import settings as app_settings
from .models import Session
from django.template.loader import render_to_string
from django.templatetags.static import static
from .report_handlers import REPORT_TYPE_CSP, REPORT_TYPE_TRIPWIRE
from .remote import create_master_session

class CspReportMiddleware:
    """The main middleware that handles all of CSP-Observer's business logic."""

    def __init__(self, get_response):
        self.super_get_response = get_response
        self.logger = logger = logging.getLogger(__name__)

        self.reporting_group_name = "csp-observer"
        self.csp_header_name = "Content-Security-Policy"
        if app_settings.REPORT_ONLY:
            self.csp_header_name = "Content-Security-Policy-Report-Only"

        # compile regexes for all enabled paths
        self.paths_regex = [re.compile("^{}$".format(p)) for p in app_settings.ENABLED_PATHS]

        nonce_temp = ''
        # generate random lower case string
        for _ in range(10):
            random_int = random.randint(97, 122)
            nonce_temp += chr(random_int)
        self.nonce = nonce_temp

    def get_response(self, request):
        response = self.super_get_response(request)
        if app_settings.IS_MASTER_COLLECTOR:
            response = self.add_cors_header(request, response)
        return response

    def anonymize_ip(self, ip_address):
        """Removes the last two octets from the ip_address."""
        return ".".join(ip_address.split(".")[:2] + 2*["0"])

    def create_session(self, request):
        """Creates a new session object, stores it in the database and returns the session id."""
        session = Session(
            user_agent=request.META["HTTP_USER_AGENT"],
            anonymized_ip=self.anonymize_ip(request.META["REMOTE_ADDR"])
        )
        session.save()
        self.logger.debug("session created: {}".format(session.id))
        return session.id

    def get_csp_policy(self, request, session_id):
        """Returns the CSP policy string based on the current settings."""
        if app_settings.REMOTE_REPORTING:
            report_uri = "{}/report/{}/{}".format(app_settings.REMOTE_CSP_OBSERVER_URL, REPORT_TYPE_CSP, session_id)
        else:
            report_uri = request.build_absolute_uri(reverse('report', args=(REPORT_TYPE_CSP, session_id, )))
        
        # set fallback reporting directive
        middleware_directives = {
            'report-uri': [report_uri],
            'script-src': ["'nonce-{}'".format(self.nonce)],
            'style-src': ["'nonce-{}'".format(self.nonce)],
            'default-src': ["'nonce-{}'".format(self.nonce)],
        }

        if app_settings.REMOTE_REPORTING:
            middleware_directives['connect-src'] = [app_settings.REMOTE_CSP_OBSERVER_URL + "/"]

        # New Reporting API stuff (not working?!):
        # https://w3c.github.io/reporting/
        # response["Reporting-Endpoints"] = '{}="{}"'.format(self.reporting_group_name, report_uri)
        report_to_group_definition = {
            "group": self.reporting_group_name,
            "max_age": 86400,
            "include_subdomains": True,
            "endpoints": [{
                "url": report_uri,
            }]
        }
        if app_settings.USE_NEW_API:
            middleware_directives['report-to'] = [self.reporting_group_name]
            response["Report-To"] = json.dumps(report_to_group_definition)

        # merge custom csp policy from settings with required middleware directives
        final_csp_policy = app_settings.CSP_POLICIES
        for directive, values in middleware_directives.items():
            if directive in final_csp_policy and directive != 'report-uri':
                final_csp_policy[directive] = set(list(final_csp_policy[directive]) + list(values))
            else:
                final_csp_policy[directive] = values
        # build csp header string
        csp_policy_string = ""
        for directive, values in final_csp_policy.items():
            csp_policy_string += "{} {}; ".format(directive, " ".join(values))

        return csp_policy_string

    def add_csp_header(self, request, response, session_id):
        """Adds the CSP header to the response."""
        policy = self.get_csp_policy(request, session_id)
        response[self.csp_header_name] = policy
        return response

    def add_cors_header(self, request, response):
        """Adds the CORS headers required for master reporting instances."""
        origins = ' '.join(app_settings.AUTHORIZED_REPORTERS)
        if 'Access-Control-Allow-Origin' in response:
            origins = response['Access-Control-Allow-Origin'] + ' ' + origins
        response['Access-Control-Allow-Origin'] = origins
        if 'Access-Control-Request-Headers' in request.headers:
            response['Access-Control-Allow-Headers'] = request.headers['Access-Control-Request-Headers']
        return response

    def add_tripwire(self, request, response, session_id):
        """Injects the tripwire javascript component into HTML response."""
        tripwire_js_path = static('csp_observer/js/tripwire.js')
        tripwire_js_uri = request.build_absolute_uri(tripwire_js_path)
        
        policy = self.get_csp_policy(request, session_id)
        policy_b64 = base64.b64encode(str.encode(policy)).decode()

        if app_settings.REMOTE_REPORTING:
            tripwire_report_uri = "{}/report/{}/{}".format(app_settings.REMOTE_CSP_OBSERVER_URL, REPORT_TYPE_TRIPWIRE, session_id)
        else:
            tripwire_report_uri = request.build_absolute_uri(reverse('report', args=(REPORT_TYPE_TRIPWIRE, session_id, )))

        script_tag_string = '<script type="text/javascript" data-session="{}" data-policy="{}" data-report-uri="{}" src="{}"></script>'.format(
            session_id, 
            policy_b64, 
            tripwire_report_uri,
            tripwire_js_uri
        )
        response.content = response.content.replace(b'</body>', str.encode(script_tag_string + '</body>'))
        return response

    def add_script_nonce(self, request, response):
        """Injects nonce attribute into all script tags in HTML response."""
        nonce_script_tag = '<script nonce="{}"'.format(self.nonce)
        response.content = response.content.replace(b'<script', str.encode(nonce_script_tag))
        return response
    
    def add_style_nonce(self, request, response):
        """Injects nonce attribute into all style and link tags in HTML response."""
        nonce_style_tag = '<style nonce="{}"'.format(self.nonce)
        response.content = response.content.replace(b'<style', str.encode(nonce_style_tag))
        nonce_link_tag = '<link nonce="{}"'.format(self.nonce)
        response.content = response.content.replace(b'<link', str.encode(nonce_link_tag))
        return response

    def add_clientui(self, request, response, session_id):
        """Injects the clientui javascript component, responsible for the popup dialog, into HTML response."""
        if app_settings.REMOTE_REPORTING:
            result_uri = "{}/result/{}".format(app_settings.REMOTE_CSP_OBSERVER_URL, session_id)
            detailpage_uri = "{}/resultdetail/{}".format(app_settings.REMOTE_CSP_OBSERVER_URL, session_id)
        else:
            result_uri = request.build_absolute_uri(reverse('result', args=(session_id, )))
            detailpage_uri = request.build_absolute_uri(reverse('result_detail', args=(session_id, )))

        clientui_html = render_to_string("client_ui/popup.html", { 
            'session_id': session_id,
            'visibility': app_settings.CLIENTUI_VISIBILITY,
            'result_uri': result_uri,
            'detailpage_uri': detailpage_uri
        })
        response.content = response.content.replace(b'</body>', str.encode(clientui_html + '</body>'))
        return response

    def __call__(self, request):
        """Checks current request path to decide if it should be observed or not."""
        # check if path in enabled paths
        for path_regex in self.paths_regex:
            if path_regex.match(request.path):
                self.logger.debug("match for path {}".format(request.path))
                if app_settings.REMOTE_REPORTING:
                    session_id = str(uuid.uuid4())
                    self.logger.debug("creating remote session {}".format(session_id))
                    asyncio.run(create_master_session(request, session_id))
                else:
                    session_id = self.create_session(request)
                request.cspo_session_id = session_id
                response = self.get_response(request)
                response = self.add_csp_header(request, response, session_id)
                response = self.add_tripwire(request, response, session_id)
                response = self.add_clientui(request, response, session_id)
                if app_settings.USE_SCRIPT_NONCE:
                    response = self.add_script_nonce(request, response)
                if app_settings.USE_STYLE_NONCE:
                    response = self.add_style_nonce(request, response)
                return response
        
        return self.get_response(request)