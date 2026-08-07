import frappe


class ProductBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def _item_group(self):

        group = frappe.db.get_value(
            "Item Group",
            {
                "custom_whmcs_group_id": str(self.snapshot["gid"])
            },
            "name",
        )

        if not group:
            raise Exception(
                f"ERP Item Group not found for WHMCS Group {self.snapshot['gid']}"
            )

        return group

    def build(self):

        item = frappe.new_doc("Item")

        item.item_code = self.snapshot["name"][:140]
        item.item_name = self.snapshot["name"][:140]

        item.item_group = self._item_group()

        item.stock_uom = "Nos"

        item.is_stock_item = 0
        item.is_sales_item = 1
        item.is_purchase_item = 0

        item.disabled = int(self.snapshot.get("retired") or 0)

        item.description = self.snapshot.get("description") or ""

        # WHMCS Mapping
        item.whmcs_pid = str(self.snapshot["id"])
        item.whmcs_product_id = str(self.snapshot["id"])
        item.custom_whmcs_product_id = str(self.snapshot["id"])
        item.custom_whmcs_group_id = str(self.snapshot["gid"])

        return item
