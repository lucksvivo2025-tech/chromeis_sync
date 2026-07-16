import frappe

from chromeis_sync.sync_engine.customer_credits.customer_credit_snapshot import CustomerCreditSnapshot
from chromeis_sync.sync_engine.customer_credits.customer_credit_router import CustomerCreditRouter
from chromeis_sync.sync_engine.customer_credits.customer_credit_validator import CustomerCreditValidator

from chromeis_sync.sync_engine.customers.customer_transaction import CustomerTransaction
from chromeis_sync.sync_engine.invoices.invoice_transaction import InvoiceTransaction


class CustomerCreditTransaction:

    def __init__(self, credit_id):
        self.credit_id = credit_id

    def execute(self):

        existing = frappe.db.get_value(
            "Journal Entry",
            {
                "custom_whmcs_credit_id": str(self.credit_id)
            },
            "name",
        )

        if existing:
            return frappe.get_doc("Journal Entry", existing)

        snapshot = CustomerCreditSnapshot.create(self.credit_id)

        valid, reason = CustomerCreditValidator(snapshot).validate()

        if not valid:
            frappe.logger().info(
                f"Customer Credit {self.credit_id} skipped: {reason}"
            )
            return None

        CustomerTransaction(snapshot["clientid"]).execute()

        if snapshot.get("relid"):
            InvoiceTransaction(snapshot["relid"]).execute()

        journal = CustomerCreditRouter.build(snapshot)

        journal.insert(ignore_permissions=True)
        journal.submit()

        frappe.db.commit()

        return journal
