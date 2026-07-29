import frappe

from .planner import PaymentReconciliationPlanner


class PaymentReconciliationInvestigator:

    def execute(self):

        planner = PaymentReconciliationPlanner()

        candidates = planner.execute()

        failures = [
            c for c in candidates
            if c.allocated_sales_invoice is None
        ]

        print()
        print("=" * 80)
        print("PAYMENT RECONCILIATION INVESTIGATION")
        print("=" * 80)
        print()

        print(f"Total Failures : {len(failures)}")
        print()

        for c in failures:

            invoices = frappe.db.sql(
                """
                SELECT
                    name,
                    docstatus,
                    whmcs_invoice_id,
                    customer
                FROM `tabSales Invoice`
                WHERE
                    whmcs_invoice_id=%s
                    OR name=%s
                ORDER BY docstatus DESC, name
                """,
                (
                    c.whmcs_invoice_id,
                    f"ACC-SINV-WH-{c.whmcs_invoice_id}",
                ),
                as_dict=True,
            )

            print("-" * 80)
            print(f"WHMCS Invoice : {c.whmcs_invoice_id}")
            print(f"Payment Entry : {c.payment_entry}")
            print(f"Customer      : {c.customer}")

            if invoices:

                print()

                for inv in invoices:

                    print(
                        inv["name"],
                        "docstatus=",
                        inv["docstatus"],
                        "whmcs_invoice_id=",
                        inv["whmcs_invoice_id"],
                    )

            else:

                print("NO ERP SALES INVOICE FOUND")

        print()
        print("=" * 80)
