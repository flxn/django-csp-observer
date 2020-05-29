from .models import CspReport

def raw_report_to_model(raw_data, session):
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