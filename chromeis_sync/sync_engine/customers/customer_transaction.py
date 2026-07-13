import frappe

from chromeis_sync.sync_engine.customers.customer_snapshot import CustomerSnapshot
from chromeis_sync.sync_engine.customers.customer_builder import CustomerBuilder


class CustomerTransaction:

    def __init__(self, userid):
        self.userid = userid

    def execute(self):

        snapshot = CustomerSnapshot.create(self.userid)

        if not snapshot:
            return None

        existing = frappe.db.get_value(
            "Customer",
            {
                "custom_whmcs_user_id": str(self.userid)
            },
            "name"
        )

        if existing:
            return frappe.get_doc("Customer", existing)

        customer = CustomerBuilder(snapshot).build()

        customer.insert(ignore_permissions=True)

        frappe.db.commit()

        return customer
