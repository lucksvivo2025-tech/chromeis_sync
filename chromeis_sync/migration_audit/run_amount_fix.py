import csv
from pathlib import Path

import frappe

from chromeis_sync.migration_audit.batch_runner import InvoiceBatchRunner


MASTER_PLAN = Path("/home/erp/migration_workspace/master_repair_plan.csv")


def execute(batch_size=None):
    """
    Execute AMOUNT_FIX repairs from the master repair plan.

    Usage:
        bench execute chromeis_sync.migration_audit.run_amount_fix.execute

    Optional:
        execute(batch_size=5)
    """

    if not MASTER_PLAN.exists():
        raise Exception(f"Master repair plan not found: {MASTER_PLAN}")

    invoices = []

    with open(MASTER_PLAN, newline="") as f:
        reader = csv.reader(f)

        for row in reader:

            if len(row) < 8:
                continue

            repair_type = row[7].strip()

            if repair_type != "AMOUNT_FIX":
                continue

            invoice_name = row[1].strip()

            if not invoice_name:
                continue

            invoices.append(invoice_name)

    print("=" * 70)
    print(f"AMOUNT_FIX invoices found : {len(invoices)}")
    print("=" * 70)

    if not invoices:
        print("Nothing to repair.")
        return

    runner = InvoiceBatchRunner(
        invoices=invoices,
        target_currency=None,
        batch_size=batch_size,
        continue_on_error=True,
    )

    result = runner.run()

    print()
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Processed : {result.stats.processed}")
    print(f"Passed    : {result.stats.passed}")
    print(f"Failed    : {result.stats.failed}")
    print(f"Skipped   : {result.stats.skipped}")
    print(f"Success % : {result.stats.success_rate}")
    print("=" * 70)

    frappe.db.commit()

    return result
