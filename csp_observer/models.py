import uuid
from django.db import models

class Session(models.Model):
    """Session model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_agent = models.CharField(max_length=255)
    anonymized_ip = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class CspRule(models.Model):
    """
    Represents a rule for evaluation of csp errors or whitelisting.
    """
    blocked_url = models.CharField(max_length=255, blank=True, null=True)
    effective_directive = models.CharField(max_length=255, blank=True, null=True)
    ignore = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

class CspReport(models.Model):
    """
    CSP Report model.
    Follows the new CSPViolationReportBody (https://w3c.github.io/webappsec-csp/#cspviolationreportbody)
    """
    session = models.ForeignKey(Session, to_field="id", on_delete=models.CASCADE)
    document_url = models.CharField(max_length=255)
    referrer = models.CharField(max_length=255, blank=True, null=True)
    blocked_url = models.CharField(max_length=255, blank=True, null=True)
    effective_directive = models.CharField(max_length=255)
    original_policy = models.CharField(max_length=255)
    source_file = models.CharField(max_length=255, blank=True, null=True)
    sample = models.CharField(max_length=255, blank=True, null=True)
    disposition = models.CharField(max_length=255)
    status_code = models.IntegerField(blank=True, null=True)
    line_number = models.IntegerField(blank=True, null=True)
    column_number = models.IntegerField(blank=True, null=True)
    matching_rules = models.ManyToManyField(CspRule, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
