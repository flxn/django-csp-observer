from django.conf import settings

NAMESPACE = getattr(settings, 'CSP_OBSERVER_NAMESPACE' , 'CSPO')
def ns_getattr(object, name, default=None):
    return getattr(settings, '_'.join([NAMESPACE, name]), default)


REPORT_ONLY = ns_getattr(settings, 'REPORT_ONLY', True)
CHECK_PATHS = ns_getattr(settings, 'CHECK_PATHS', ["/"])

CSP_POLICIES = ns_getattr(settings, 'CSP_POLICIES', [
    "default-src 'self'",
])