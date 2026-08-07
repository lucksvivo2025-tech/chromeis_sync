import frappe


class ServicePlanner:

    @staticmethod
    def pending(limit=100):

        return frappe.db.sql(
            """
            SELECT s.id
            FROM whmcs_mirror.tblhosting s

            LEFT JOIN `tabWHMCS Service` ws
                ON ws.whmcs_service_id = CAST(s.id AS CHAR)

            WHERE ws.name IS NULL

            ORDER BY s.id

            LIMIT %s
            """,
            (limit,),
            pluck=True,
        )
