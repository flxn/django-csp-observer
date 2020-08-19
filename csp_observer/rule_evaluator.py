from .models import CspRule, GlobalCspRule

class CspRuleEvaluator(object):

    def __init__(self):
        custom_rules = list(CspRule.objects.all())
        global_rules = list(GlobalCspRule.objects.all())
        self.rules = custom_rules + global_rules
    
    def evaluate_directive(self, url, directive):
        """Evaluates a url and directive against all rules.
        Does not differentiate between general and element directives (script-src == script-src-elem).
        Returns list of matching rules and ignore flag if the report is blacklisted"""
        matching_rules = []
        ignore = False
        for rule in self.rules:
            if rule.blocked_url == url:
                if rule.effective_directive == None or rule.effective_directive.replace('-elem', '') == directive.replace('-elem', ''):
                    matching_rules.append(rule)
                    if rule.ignore:
                        ignore = True
        return (matching_rules, ignore)

    def evaluate_report(self, csp_report):
        """Evaluates a CSP report against all rules.
        Returns list of matching rules and ignore flag if the report is blacklisted"""
        return self.evaluate_directive(csp_report.blocked_url, csp_report.effective_directive)