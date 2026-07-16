import frappe

from chromeis_sync.sync_engine.invoices.invoice_snapshot import InvoiceSnapshot
from chromeis_sync.sync_engine.invoices.invoice_builder import InvoiceBuilder
from chromeis_sync.sync_engine.customers.customer_transaction import CustomerTransaction


class InvoiceTransaction:

    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def execute(self):

        existing = frappe.db.get_value(
            "Sales Invoice",
            {"whmcs_invoice_id": str(self.invoice_id)},
            "name",
        )

        if existing:
            return frappe.get_doc("Sales Invoice", existing)

        snapshot = InvoiceSnapshot.create(self.invoice_id)

        # Skip invoices that have no invoice items
        if not snapshot.get("items"):
            frappe.logger().info(
                f"Skipping WHMCS Invoice {self.invoice_id}: no invoice items."
            )
            return None

        customer = frappe.db.get_value(
            "Customer",
            {"custom_whmcs_user_id": str(snapshot["userid"])},
            "name",
        )

        if not customer:
            CustomerTransaction(snapshot["userid"]).execute()

            customer = frappe.db.get_value(
                "Customer",
                {"custom_whmcs_user_id": str(snapshot["userid"])},
                "name",
            )

        invoice = InvoiceBuilder(snapshot).build()

        invoice.insert(ignore_permissions=True)

        if snapshot.get("status") == "Paid":
            invoice.submit()

        frappe.db.commit()

        return invoice
