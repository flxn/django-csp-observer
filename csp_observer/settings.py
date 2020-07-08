from django.conf import settings

NAMESPACE = getattr(settings, 'CSP_OBSERVER_NAMESPACE' , 'CSPO')
def ns_getattr(object, name, default=None):
    return getattr(settings, '_'.join([NAMESPACE, name]), default)

REPORT_ONLY = ns_getattr(settings, 'REPORT_ONLY', True)
ENABLED_PATHS = ns_getattr(settings, 'ENABLED_PATHS', [
    "/"
])

CSP_POLICIES = ns_getattr(settings, 'CSP_POLICIES', [
    "default-src 'self'; script-src 'self' 'unsafe-inline';",
])

ENABLE_NEW_API = ns_getattr(settings, 'ENABLE_NEW_API', False)
RESULT_WAIT_TIME = 10

SESSION_KEEP_DAYS = 14

IS_MASTER_COLLECTOR = False
AUTHORIZED_REPORTERS = []

REMOTE_REPORTING = False
REMOTE_CSP_OBSERVER_URL = ""
