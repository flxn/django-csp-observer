from django import template
from django.urls import reverse
from csp_observer import settings as app_settings
from csp_observer.report_handlers import REPORT_TYPE_CSP, REPORT_TYPE_TRIPWIRE

register = template.Library()

@register.inclusion_tag('result_tag.html', takes_context=True)
def csp_check_result(context):
    request = context['request']
    if app_settings.REMOTE_REPORTING:
        iframe_url = "{}/result/{}".format(app_settings.REMOTE_CSP_OBSERVER_URL, request.cspo_session_id)
    else:
        iframe_url = request.build_absolute_uri(reverse('result', args=(request.cspo_session_id, )))
    
    return {
        'request': request,
        'result_iframe_url': iframe_url
    }