import frappe


class PaymentSnapshot:

    @staticmethod
    def create(account_id):

        rows = frappe.db.sql("""
            SELECT *
            FROM whmcs_mirror.tblaccounts
            WHERE id=%s
        """, account_id, as_dict=True)

        if not rows:
            raise Exception(
                f"Payment {account_id} not found."
            )

        payment = rows[0]

        invoice = None

        if payment["invoiceid"]:

            invoices = frappe.db.sql("""
                SELECT
                    name,
                    whmcs_invoice_id,
                    customer,
                    currency,
                    grand_total,
                    outstanding_amount,
                    docstatus
                FROM `tabSales Invoice`
                WHERE whmcs_invoice_id=%s
            """, payment["invoiceid"], as_dict=True)

            if invoices:
                invoice = invoices[0]

        return {
            "payment": payment,
            "invoice": invoice,
        }
