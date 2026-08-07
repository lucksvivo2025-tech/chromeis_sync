import frappe


class ServerSnapshot:

    @staticmethod
    def create(server_id):

        server = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblservers
            WHERE id=%s
            """,
            (server_id,),
            as_dict=True,
        )

        if not server:
            return None

        return server[0]
