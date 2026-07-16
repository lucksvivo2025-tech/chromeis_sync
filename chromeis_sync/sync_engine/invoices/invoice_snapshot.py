import frappe


class InvoiceSnapshot:

    @staticmethod
    def create(invoice_id):

        invoice = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
            """,
            (invoice_id,),
            as_dict=True,
        )

        if not invoice:
            raise Exception(f"WHMCS Invoice {invoice_id} not found")

        invoice = invoice[0]

        customer = frappe.db.sql(
            """
            SELECT
                id,
                firstname,
                lastname,
                companyname,
                email
            FROM whmcs_mirror.tblclients
            WHERE id=%s
            """,
            (invoice["userid"],),
            as_dict=True,
        )

        invoice["customer"] = customer[0] if customer else {}

        items = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
            """,
            (invoice_id,),
            as_dict=True,
        )

        invoice["items"] = items

        return invoice
