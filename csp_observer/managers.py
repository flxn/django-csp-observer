from django.db import models

class CspRuleManager(models.Manager):
    """Django model manager for convenient query of global and custom rules."""
    def get_global(self):
        return super().get_queryset().exclude(global_id=None)

    def get_custom(self):
        return super().get_queryset().filter(global_id=None)