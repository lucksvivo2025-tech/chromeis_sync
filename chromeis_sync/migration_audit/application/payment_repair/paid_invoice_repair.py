import frappe

from collections import Counter

from chromeis_sync.migration_audit.infrastructure.whmcs import WHMCSDatabase
from chromeis_sync.migration_audit.application.invoice_reconciliation_engine import (
    InvoiceReconciliationEngine,
)


class PaidInvoiceRepair:

    def __init__(self):
        self.engine = InvoiceReconciliationEngine()

    def whmcs_query(self, sql, params=()):
        return WHMCSDatabase.query(sql, params)

    def get_paid_invoices(self):
        return self.whmcs_query("""
            SELECT
                id,
                userid,
                status,
                subtotal,
                credit,
                tax,
                total
            FROM tblinvoices
            WHERE status = 'Paid'
            ORDER BY id
        """)

    def get_erp_invoice(self, whmcs_invoice_id):

        return frappe.db.get_value(
            "Sales Invoice",
            {"whmcs_invoice_id": str(whmcs_invoice_id)},
            [
                "name",
                "status",
                "docstatus",
                "outstanding_amount",
            ],
            as_dict=True,
        )

    def process_invoice(self, invoice):

        erp = self.get_erp_invoice(invoice.id)

        if not erp:
            return "missing", None

        if erp.docstatus == 2:
            return "cancelled", None

        expected = self.engine.expected_erp_statuses(invoice)

        if erp.status in expected:
            return "correct", None

        return (
            "needs_repair",
            {
                "invoice": invoice.id,
                "whmcs_status": invoice.status,
                "erp_status": erp.status,
                "expected": list(expected),
                "docstatus": erp.docstatus,
                "outstanding": erp.outstanding_amount,
                "erp": erp,
            },
        )

    def execute(self):

        rows = self.get_paid_invoices()

        invoices = self.engine.classify_invoices(rows)

        print(f"Paid invoices loaded : {len(invoices)}")

        correct = 0
        needs_repair = 0
        missing = 0
        cancelled = 0

        status_counter = Counter()
        expected_counter = Counter()

        for invoice in invoices:

            result, details = self.process_invoice(invoice)

            if result == "correct":
                correct += 1

            elif result == "missing":
                missing += 1

            elif result == "cancelled":
                cancelled += 1

            elif result == "needs_repair":

                needs_repair += 1

                status_counter[details["erp_status"]] += 1

                expected = tuple(sorted(details["expected"]))
                expected_counter[expected] += 1

                if needs_repair <= 20:
                    print(details)

        print()
        print("Repair Categories")
        print("-----------------")

        for status, count in sorted(
            status_counter.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            print(f"{status:<20} {count}")

        print()
        print("Expected Status Sets")
        print("--------------------")

        for expected, count in sorted(
            expected_counter.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            print(f"{list(expected)!s:<30} {count}")

        print()
        print(f"Correct            : {correct}")
        print(f"Needs Repair       : {needs_repair}")
        print(f"Missing            : {missing}")
        print(f"Cancelled          : {cancelled}")

        return {
            "paid_invoices_loaded": len(invoices),
            "correct": correct,
            "needs_repair": needs_repair,
            "missing": missing,
            "cancelled": cancelled,
        }


def run():
    return PaidInvoiceRepair().execute()
