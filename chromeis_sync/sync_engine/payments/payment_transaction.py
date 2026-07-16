import frappe

from chromeis_sync.sync_engine.payments.payment_snapshot import PaymentSnapshot
from chromeis_sync.sync_engine.payments.payment_builder import PaymentBuilder


class PaymentTransaction:

    def __init__(self, payment_id):
        self.payment_id = payment_id

    def execute(self):

        # --------------------------------------------------------
        # Skip if already imported
        # --------------------------------------------------------

        existing = frappe.db.get_value(
            "Payment Entry",
            {
                "custom_whmcs_txn_id": str(self.payment_id)
            },
            "name",
        )

        if existing:
            return frappe.get_doc("Payment Entry", existing)

        # --------------------------------------------------------
        # Snapshot
        # --------------------------------------------------------

        snapshot = PaymentSnapshot.create(self.payment_id)

        if not snapshot.get("invoiceid"):
            frappe.logger().info(
                f"Skipping WHMCS Payment {self.payment_id}: invoiceid = 0"
            )
            return None

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(snapshot["invoiceid"])
            },
            "name",
        )

        if not invoice:
            raise Exception(
                f"ERP Invoice not found for WHMCS Invoice {snapshot['invoiceid']}"
            )

        invoice_doc = frappe.get_doc("Sales Invoice", invoice)

        # --------------------------------------------------------
        # Skip already-settled invoices
        # --------------------------------------------------------

        if abs(invoice_doc.outstanding_amount or 0) < 0.0001:

            frappe.logger().warning(
                f"""
WHMCS Payment {self.payment_id}

Invoice : {snapshot['invoiceid']}
ERP     : {invoice}

Skipped because ERP invoice already has zero outstanding.

WHMCS remains the source of truth.
This invoice should be reviewed during reconciliation.
"""
            )

            return None

        # --------------------------------------------------------
        # Build Payment
        # --------------------------------------------------------

        payment = PaymentBuilder(snapshot).build()

        print("\n" + "=" * 70)
        print(f"WHMCS Payment ID : {self.payment_id}")
        print(f"ERP Invoice      : {invoice}")
        print(f"References Found : {len(payment.references)}")

        if payment.references:
            for ref in payment.references:
                print(
                    f" -> {ref.reference_name} | "
                    f"Allocated={ref.allocated_amount}"
                )
        else:
            print(" -> NO REFERENCES CREATED")

        print("=" * 70 + "\n")

        payment.custom_whmcs_txn_id = str(self.payment_id)

        # --------------------------------------------------------
        # Insert
        # --------------------------------------------------------

        payment.insert(ignore_permissions=True)

        print(
            f"Inserted Payment Entry : {payment.name}"
        )

        print(
            f"References AFTER INSERT : {len(payment.references)}"
        )

        if payment.references:
            for ref in payment.references:
                print(
                    f" -> {ref.reference_name} | "
                    f"Allocated={ref.allocated_amount}"
                )
        else:
            print(" -> NO REFERENCES AFTER INSERT")

        # --------------------------------------------------------
        # Submit
        # --------------------------------------------------------

        payment.submit()

        print(
            f"References AFTER SUBMIT : {len(payment.references)}"
        )

        if payment.references:
            for ref in payment.references:
                print(
                    f" -> {ref.reference_name} | "
                    f"Allocated={ref.allocated_amount}"
                )
        else:
            print(" -> NO REFERENCES AFTER SUBMIT")

        frappe.db.commit()

        return payment
