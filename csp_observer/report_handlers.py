import logging
from .models import CspReport
from .rule_evaluator import CspRuleEvaluator
from .models import CspReport, Session

REPORT_TYPE_CSP = 'csp'
REPORT_TYPE_TRIPWIRE = 'tripwire'

logger = logging.getLogger(__name__)

def raw_csp_report_to_model(raw_data, session):
    """Takes raw csp report data and session object and creates a base CspReport model without saving"""
    report = CspReport()

    report.session = session

    if 'document-url' in raw_data:
        report.document_url = raw_data['document-url']
    else:
        report.blocked_url = raw_data.get('document-uri')

    if 'blocked-url' in raw_data:
        report.blocked_url = raw_data['blocked-url']
    else:
        report.blocked_url = raw_data.get('blocked-uri')

    report.referrer = raw_data.get('referrer')
    report.effective_directive = raw_data.get('effective-directive')
    report.original_policy = raw_data.get('original-policy')
    report.source_file = raw_data.get('source-file')
    report.sample = raw_data.get('sample')
    report.disposition = raw_data.get('disposition')
    report.status_code = raw_data.get('status-code')
    report.line_number = raw_data.get('line-number')
    report.column_number = raw_data.get('column-number')

    return report

def handle_csp_report(report_data, session_id):
    if not 'csp-report' in report_data:
        return

    csp_report_raw = report_data['csp-report']
    logger.info("Received CSP report")
    logger.info("Session ID: {}".format(session_id))
    logger.info("Report Data: {}".format(csp_report_raw))

    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return
    else:
        report = raw_csp_report_to_model(csp_report_raw, session)
        evaluator = CspRuleEvaluator()
        has_been_added = evaluator.evaluate_and_save(report)
        if has_been_added:
            logger.info("Report saved with id {}".format(report.id))
        else:
            logger.info("Report will be ignored")
    
def handle_tripwire_report(report_data, session_id):
    logger.info("Received Tripwire report")
    logger.info("Report Data: {}".format(report_data))