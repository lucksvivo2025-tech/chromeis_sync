import frappe


class GroupPlanner:

    @staticmethod
    def pending(limit=100):

        return frappe.db.sql(
            """
            SELECT g.id
            FROM whmcs_mirror.tblproductgroups g

            LEFT JOIN `tabItem Group` ig
                ON ig.custom_whmcs_group_id = CAST(g.id AS CHAR)

            WHERE ig.name IS NULL

            ORDER BY g.id

            LIMIT %s
            """,
            (limit,),
            pluck=True,
        )
