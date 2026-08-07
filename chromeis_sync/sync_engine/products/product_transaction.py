import frappe

from chromeis_sync.sync_engine.products.product_snapshot import ProductSnapshot
from chromeis_sync.sync_engine.products.product_builder import ProductBuilder


class ProductTransaction:

    def __init__(self, product_id):
        self.product_id = product_id

    def execute(self):

        snapshot = ProductSnapshot.create(self.product_id)

        if not snapshot:
            return None

        # Existing mapping
        existing = frappe.db.get_value(
            "Item",
            {
                "whmcs_pid": str(self.product_id)
            },
            "name",
        )

        # Fallback to legacy/custom fields
        if not existing:
            existing = frappe.db.get_value(
                "Item",
                {
                    "whmcs_product_id": str(self.product_id)
                },
                "name",
            )

        if not existing:
            existing = frappe.db.get_value(
                "Item",
                {
                    "custom_whmcs_product_id": str(self.product_id)
                },
                "name",
            )

        if existing:
            item = frappe.get_doc("Item", existing)

            # Ensure all mapping fields are populated
            updates = {}

            if not item.whmcs_pid:
                updates["whmcs_pid"] = str(self.product_id)

            if not item.whmcs_product_id:
                updates["whmcs_product_id"] = str(self.product_id)

            if not item.custom_whmcs_product_id:
                updates["custom_whmcs_product_id"] = str(self.product_id)

            if not item.custom_whmcs_group_id:
                updates["custom_whmcs_group_id"] = str(snapshot["gid"])

            if updates:
                frappe.db.set_value("Item", existing, updates)
                frappe.db.commit()

            return item

        item = ProductBuilder(snapshot).build()

        item.insert(ignore_permissions=True)

        frappe.db.commit()

        return item
