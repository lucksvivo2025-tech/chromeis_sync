import frappe


class GroupSnapshot:

    @staticmethod
    def create(group_id):

        group = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblproductgroups
            WHERE id=%s
            """,
            (group_id,),
            as_dict=True,
        )

        if not group:
            return None

        return group[0]
