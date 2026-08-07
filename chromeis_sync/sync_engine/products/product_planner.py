import frappe


class ProductPlanner:

    @staticmethod
    def pending(limit=100):

        return frappe.db.sql(
            """
            SELECT p.id
            FROM whmcs_mirror.tblproducts p

            LEFT JOIN `tabItem` i
                ON i.whmcs_product_id = CAST(p.id AS CHAR)

            WHERE i.name IS NULL

            ORDER BY p.id

            LIMIT %s
            """,
            (limit,),
            pluck=True,
        )
