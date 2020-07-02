from .models import CspRule

class CspRuleEvaluator(object):

    def __init__(self):
        self.rules = CspRule.objects.all()
    
    def evaluate(self, csp_report):
        """Evaluates a CSP report against all rules.
        Returns list of matching rules or None if the report is blacklisted"""
        matching_rules = []
        for rule in self.rules:
            if rule.blocked_url == csp_report.blocked_url and rule.effective_directive == csp_report.effective_directive:
                matching_rules.append(rule)
                if rule.ignore:
                    return None
        return matching_rules

    def evaluate_and_save(self, csp_report):
        """Evaluates a CSP report and stores it in the database."""
        matching_rules = self.evaluate(csp_report)

        if matching_rules == None:
            # report should be ignored
            return False
        
        csp_report.save()    
        csp_report.matching_rules.add(*matching_rules)

        return True
