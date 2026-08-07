import frappe

from chromeis_sync.sync_engine.services.service_snapshot import ServiceSnapshot
from chromeis_sync.sync_engine.services.service_builder import ServiceBuilder


class ServiceTransaction:

    def __init__(self, service_id):
        self.service_id = service_id

    def execute(self):

        snapshot = ServiceSnapshot.create(self.service_id)

        if not snapshot:
            return None

        existing = frappe.db.get_value(
            "WHMCS Service",
            {
                "whmcs_service_id": str(self.service_id)
            },
            "name",
        )

        if existing:

            service = frappe.get_doc(
                "WHMCS Service",
                existing
            )

            updates = {}

            for field in [

                "whmcs_user_id",
                "customer_name",
                "domain",
                "product_name",
                "status",
                "billing_cycle",
                "next_due_date",
                "amount",
                "username",
                "dedicated_ip",
                "client_deleted",
                "product_deleted",
            ]:

                value = ServiceBuilder(snapshot).build().get(field)

                if value is not None:
                    updates[field] = value

            if updates:
                frappe.db.set_value(
                    "WHMCS Service",
                    existing,
                    updates
                )

                frappe.db.commit()

            return service


        service = ServiceBuilder(snapshot).build()

        service.insert(
            ignore_permissions=True
        )

        frappe.db.commit()

        return service
