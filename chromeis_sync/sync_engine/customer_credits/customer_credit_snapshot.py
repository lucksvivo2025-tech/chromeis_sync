import frappe


class CustomerCreditSnapshot:

    @staticmethod
    def create(credit_id):

        credit = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblcredit
            WHERE id=%s
            """,
            credit_id,
            as_dict=True,
        )

        if not credit:
            raise Exception(
                f"WHMCS Credit {credit_id} not found."
            )

        credit = credit[0]

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
            credit["clientid"],
            as_dict=True,
        )

        credit["customer"] = customer[0] if customer else None

        return credit
