import re
from .models import CspRule

class CspRuleEvaluator(object):

    def __init__(self):
        self.rules = list(CspRule.objects.all())
    
    def evaluate_directive(self, url, directive):
        """Evaluates a url and directive against all rules.

        Does not differentiate between general and element directives (script-src == script-src-elem).
        Returns list of matching rules and ignore flag if the report is blacklisted.
        """
        matching_rules = []
        ignore = False
        if not url:
            return (matching_rules, ignore)
        for rule in self.rules:
            if re.match(rule.blocked_url, url):
                # url matches, now check directive if rule requires matching directive
                if (not rule.effective_directive) or (rule.effective_directive and rule.effective_directive.replace('-elem', '') == directive.replace('-elem', '')):
                    matching_rules.append(rule)
                    if rule.ignore:
                        ignore = True
        return (matching_rules, ignore)

    def evaluate_report(self, csp_report):
        """Evaluates a CSP report against all rules.

        Returns list of matching rules and ignore flag if the report is blacklisted.
        """
        return self.evaluate_directive(csp_report.blocked_url, csp_report.effective_directive)