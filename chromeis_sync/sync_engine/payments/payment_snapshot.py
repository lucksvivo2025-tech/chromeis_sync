import frappe


class PaymentSnapshot:

    @staticmethod
    def create(payment_id):

        payment = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblaccounts
            WHERE id=%s
            """,
            (payment_id,),
            as_dict=True,
        )

        if not payment:
            raise Exception(f"WHMCS Payment {payment_id} not found")

        payment = payment[0]

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
            (payment["userid"],),
            as_dict=True,
        )

        payment["customer"] = customer[0] if customer else {}

        invoice = frappe.db.sql(
            """
            SELECT
                id,
                userid,
                status,
                total,
                date,
                duedate
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
            """,
            (payment["invoiceid"],),
            as_dict=True,
        )

        payment["invoice"] = invoice[0] if invoice else {}

        return payment
