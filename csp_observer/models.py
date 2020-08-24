import uuid
from django.db import models
from .managers import CspRuleManager

class Session(models.Model):
    """Represents a single user session (a page access)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_agent = models.CharField(max_length=255)
    anonymized_ip = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}@{}".format(self.id, self.created_at)

class CspRule(models.Model):
    """Represents a rule for evaluation of csp errors or whitelisting."""
    CAUSES = (
        ('extension', 'Browser Extension'),
        ('browser', 'Web Browser'),
        ('malware', 'Malware'),
        ('other', 'Other'),
    )

    global_id = models.CharField(max_length=255, blank=True, null=True)
    blocked_url = models.CharField(max_length=255, blank=True, null=True)
    effective_directive = models.CharField(max_length=255, blank=True, null=True)
    ignore = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    cause = models.CharField(max_length=255, choices=CAUSES, default='other')

    objects = CspRuleManager()

    def __str__(self):
        return "{} {} ({}) {}".format(self.global_id if self.global_id else "", self.title, self.blocked_url, "[Ignore]" if self.ignore else "")

class CspReport(models.Model):
    """CSP Report model.

    Follows the new CSPViolationReportBody (https://w3c.github.io/webappsec-csp/#cspviolationreportbody)
    """
    session = models.ForeignKey(Session, to_field="id", on_delete=models.CASCADE)
    document_url = models.CharField(max_length=255)
    referrer = models.CharField(max_length=255, blank=True, null=True)
    blocked_url = models.CharField(max_length=255, blank=True, null=True)
    effective_directive = models.CharField(max_length=255)
    original_policy = models.CharField(max_length=255, blank=True, null=True)
    source_file = models.CharField(max_length=255, blank=True, null=True)
    sample = models.CharField(max_length=255, blank=True, null=True)
    disposition = models.CharField(max_length=255, blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    line_number = models.IntegerField(blank=True, null=True)
    column_number = models.IntegerField(blank=True, null=True)
    matching_rules = models.ManyToManyField(CspRule, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}@{}".format(self.blocked_url, self.session)

class StoredConfig(models.Model):
    """Generic model for storing key/value pairs."""
    key = models.TextField(unique=True)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}={}".format(self.key, self.value)