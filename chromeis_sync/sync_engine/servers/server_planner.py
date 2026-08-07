import frappe


class ServerPlanner:

    @staticmethod
    def pending(limit=100):

        return frappe.db.sql(
            """
            SELECT s.id
            FROM whmcs_mirror.tblservers s

            LEFT JOIN `tabServer` srv
                ON srv.whmcs_id = CAST(s.id AS CHAR)

            WHERE srv.name IS NULL

            ORDER BY s.id

            LIMIT %s
            """,
            (limit,),
            pluck=True,
        )
