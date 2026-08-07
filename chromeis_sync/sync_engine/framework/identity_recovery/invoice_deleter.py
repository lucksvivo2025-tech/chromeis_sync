import frappe


class InvoiceDeleter:

    @staticmethod
    def delete(invoice):

        frappe.delete_doc(
            "Sales Invoice",
            invoice.name,
            force=True,
            ignore_permissions=True,
        )
