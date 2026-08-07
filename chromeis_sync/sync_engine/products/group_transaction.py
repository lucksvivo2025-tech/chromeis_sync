import frappe

from chromeis_sync.sync_engine.products.group_snapshot import GroupSnapshot
from chromeis_sync.sync_engine.products.group_builder import GroupBuilder


class GroupTransaction:

    def __init__(self, group_id):
        self.group_id = group_id

    def execute(self):

        snapshot = GroupSnapshot.create(self.group_id)

        if not snapshot:
            return None

        # First try WHMCS mapping
        existing = frappe.db.get_value(
            "Item Group",
            {
                "custom_whmcs_group_id": str(self.group_id)
            },
            "name",
        )

        # Then fall back to name match
        if not existing:
            existing = frappe.db.get_value(
                "Item Group",
                {
                    "item_group_name": snapshot["name"][:140]
                },
                "name",
            )

            if existing:
                frappe.db.set_value(
                    "Item Group",
                    existing,
                    "custom_whmcs_group_id",
                    str(self.group_id),
                )
                frappe.db.commit()

        if existing:
            return frappe.get_doc("Item Group", existing)

        group = GroupBuilder(snapshot).build()

        group.insert(ignore_permissions=True)

        frappe.db.commit()

        return group
