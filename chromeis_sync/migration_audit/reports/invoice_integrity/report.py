from __future__ import annotations

from chromeis_sync.migration_audit.application.invoice_integrity_engine import (
    InvoiceIntegrityEngine,
)
from chromeis_sync.migration_audit.reports.core.base_report import BaseReport

import frappe


class InvoiceIntegrityReport(BaseReport):
    """
    R001 - WHMCS Invoice Integrity Report

    Validates that every WHMCS invoice is internally
    financially consistent.

        Header Total == Sum(Invoice Items)

    This report ONLY validates WHMCS.

    It does NOT compare against ERP.
    """

    report_id = "R001"

    report_name = "Invoice Integrity Report"

    def __init__(self):

        super().__init__()

        self.engine = InvoiceIntegrityEngine()

    # ----------------------------------------------------------
    # Data
    # ----------------------------------------------------------

    def load_invoice_ids(self) -> list[int]:

        rows = frappe.db.sql(
            """
            SELECT id
            FROM whmcs_mirror.tblinvoices
            ORDER BY id
            """,
            as_dict=True,
        )

        return [row["id"] for row in rows]

    # ----------------------------------------------------------
    # Execution
    # ----------------------------------------------------------

    def execute(self):

        self.start()

        invoice_ids = self.load_invoice_ids()

        print()
        print("=" * 70)
        print(self.report_name)
        print("=" * 70)
        print(f"Invoices Found : {len(invoice_ids)}")
        print()

        exact = 0
        header_gt = 0
        items_gt = 0

        for invoice_id in invoice_ids:

            result = self.engine.validate(invoice_id)

            if result.status == "EXACT_MATCH":

                exact += 1

                self.pass_check(
                    f"Invoice {result.invoice_id}"
                )

            elif result.status == "HEADER_GREATER_THAN_ITEMS":

                header_gt += 1

                self.fail_check(
                    f"Invoice {result.invoice_id}",
                    notes=(
                        f"Header={result.header_total} "
                        f"Items={result.item_total} "
                        f"Difference={result.difference}"
                    ),
                )

                self.add_exception(
                    category="HEADER_GREATER_THAN_ITEMS",
                    invoice_id=result.invoice_id,
                    header_total=str(result.header_total),
                    item_total=str(result.item_total),
                    difference=str(result.difference),
                )

            else:

                items_gt += 1

                self.fail_check(
                    f"Invoice {result.invoice_id}",
                    notes=(
                        f"Header={result.header_total} "
                        f"Items={result.item_total} "
                        f"Difference={result.difference}"
                    ),
                )

                self.add_exception(
                    category="ITEMS_GREATER_THAN_HEADER",
                    invoice_id=result.invoice_id,
                    header_total=str(result.header_total),
                    item_total=str(result.item_total),
                    difference=str(result.difference),
                )

        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)

        print(f"Exact Match                : {exact}")
        print(f"Header Greater Than Items  : {header_gt}")
        print(f"Items Greater Than Header  : {items_gt}")
        print(f"Total Invoices             : {len(invoice_ids)}")

        self.print_audit_summary()

        self.finish()

        return {
            "report_id": self.report_id,
            "report_name": self.report_name,
            "total_invoices": len(invoice_ids),
            "exact_match": exact,
            "header_greater_than_items": header_gt,
            "items_greater_than_header": items_gt,
            "pass": self.pass_count,
            "warn": self.warn_count,
            "fail": self.fail_count,
            "exceptions": self.exceptions,
            "results": self.results,
        }


def run():

    report = InvoiceIntegrityReport()

    return report.execute()
