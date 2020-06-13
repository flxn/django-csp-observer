from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig

class CspObserverConfig(AppConfig):
    name = 'csp_observer'

class CspObserverAdminConfig(AdminConfig):
    default_site = 'csp_observer.admin.CspObserverAdminSite'