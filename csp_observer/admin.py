from django.contrib import admin
from .models import CspRule, StoredConfig

admin.site.register(CspRule)
admin.site.register(StoredConfig)