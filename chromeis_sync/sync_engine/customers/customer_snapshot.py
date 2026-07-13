import frappe


class CustomerSnapshot:

    @staticmethod
    def create(userid):

        customer = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblclients
            WHERE id=%s
            """,
            userid,
            as_dict=True,
        )

        if not customer:
            return None

        return customer[0]
