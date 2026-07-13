import frappe


class CustomerPlanner:

    @staticmethod
    def pending(limit=100):
        return frappe.db.sql(
            """
            SELECT c.id
            FROM whmcs_mirror.tblclients c
            LEFT JOIN `tabCustomer` cust
                ON cust.whmcs_id = CAST(c.id AS CHAR)
            WHERE cust.name IS NULL
            ORDER BY c.id
            LIMIT %s
            """,
            (limit,),
            pluck=True,
        )
