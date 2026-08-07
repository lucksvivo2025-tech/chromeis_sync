import frappe


class GroupBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        group = frappe.new_doc("Item Group")

        group.item_group_name = self.snapshot["name"][:140]
        group.parent_item_group = "All Item Groups"
        group.is_group = 1

        group.custom_whmcs_group_id = str(self.snapshot["id"])

        return group
