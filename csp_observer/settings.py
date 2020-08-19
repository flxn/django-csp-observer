from django.conf import settings

NAMESPACE = getattr(settings, 'CSP_OBSERVER_NAMESPACE' , 'CSPO')
def ns_getattr(object, name, default=None):
    return getattr(settings, '_'.join([NAMESPACE, name]), default)

REPORT_ONLY = ns_getattr(settings, 'REPORT_ONLY', True)
ENABLED_PATHS = ns_getattr(settings, 'ENABLED_PATHS', [
    "/"
])

CSP_POLICIES = ns_getattr(settings, 'CSP_POLICIES', {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'"],
    'connect-src': ["'self'"],
    'style-src-attr': ["'unsafe-inline'"],
})

USE_NEW_API = ns_getattr(settings, 'USE_NEW_API', False)
RESULT_WAIT_TIME = ns_getattr(settings, 'RESULT_WAIT_TIME', 10)
USE_SCRIPT_NONCE = ns_getattr(settings, 'USE_SCRIPT_NONCE', True)
USE_STYLE_NONCE = ns_getattr(settings, 'USE_STYLE_NONCE', True)

SESSION_KEEP_DAYS = ns_getattr(settings, 'SESSION_KEEP_DAYS', 14)

IS_MASTER_COLLECTOR = ns_getattr(settings, 'IS_MASTER_COLLECTOR', False)
AUTHORIZED_REPORTERS = ns_getattr(settings, 'AUTHORIZED_REPORTERS', [])
REMOTE_SECRET = ns_getattr(settings, 'REMOTE_SECRET', '')
REMOTE_REPORTING = ns_getattr(settings, 'REMOTE_REPORTING', False)
REMOTE_CSP_OBSERVER_URL = ns_getattr(settings, 'REMOTE_CSP_OBSERVER_URL', "").rstrip('/')

CLIENTUI_VISIBILITY = ns_getattr(settings, 'CLIENTUI_VISIBILITY', 'always')

RULE_UPDATE_FILE = ns_getattr(settings, 'RULE_UPDATE_FILE', 'https://raw.githubusercontent.com/flxn/csp-observer-data/master/rules.json')