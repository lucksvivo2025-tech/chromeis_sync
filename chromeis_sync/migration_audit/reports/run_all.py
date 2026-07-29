from chromeis_sync.migration_audit.reports.invoice_integrity.report import (
    InvoiceIntegrityReport,
)


def run():
    print("\n" + "=" * 80)
    print("CHROMEIS MIGRATION AUDIT SUITE")
    print("=" * 80)

    reports = [
        InvoiceIntegrityReport(),
    ]

    results = {}

    for report in reports:
        print(f"\nRunning {report.report_id} - {report.report_name}")
        results[report.report_id] = report.execute()

    print("\n" + "=" * 80)
    print("AUDIT SUITE COMPLETE")
    print("=" * 80)

    return results
