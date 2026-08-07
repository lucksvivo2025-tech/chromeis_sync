import frappe


class InvoiceItemIdentityResolver:

    @staticmethod
    def by_whmcs_item_id(whmcs_item_id):

        return frappe.db.get_value(
            "Sales Invoice Item",
            {
                "whmcs_item_id": str(
                    whmcs_item_id,
                ),
            },
            "name",
        )

    @staticmethod
    def exists(whmcs_item_id):

        return bool(
            InvoiceItemIdentityResolver.by_whmcs_item_id(
                whmcs_item_id,
            )
        )

    @staticmethod
    def get(whmcs_item_id):

        name = (
            InvoiceItemIdentityResolver.by_whmcs_item_id(
                whmcs_item_id,
            )
        )

        if not name:

            return None

        return frappe.get_doc(
            "Sales Invoice Item",
            name,
        )
