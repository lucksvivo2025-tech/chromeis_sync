import frappe


class InvoiceIdentityResolver:

    @staticmethod
    def by_whmcs_invoice_id(invoice_id):

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(invoice_id),
            },
            "name",
        )

        if invoice:

            return invoice

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_inv_id": str(invoice_id),
            },
            "name",
        )

        if invoice:

            return invoice

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "custom_whmcs_invoice_id": str(invoice_id),
            },
            "name",
        )

        return invoice

    @staticmethod
    def get(invoice_id):

        invoice = InvoiceIdentityResolver.by_whmcs_invoice_id(
            invoice_id
        )

        if not invoice:

            return None

        return frappe.get_doc(
            "Sales Invoice",
            invoice,
        )

    @staticmethod
    def exists(invoice_id):

        return (
            InvoiceIdentityResolver.by_whmcs_invoice_id(
                invoice_id
            )
            is not None
        )
