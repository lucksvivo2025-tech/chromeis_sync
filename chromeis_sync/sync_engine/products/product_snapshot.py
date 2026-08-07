import frappe


class ProductSnapshot:

    @staticmethod
    def create(product_id):

        product = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblproducts
            WHERE id=%s
            """,
            (product_id,),
            as_dict=True,
        )

        if not product:
            return None

        return product[0]
