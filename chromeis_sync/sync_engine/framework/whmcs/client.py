import frappe


class WHMCSClient:
    """
    Generic read-only client for the WHMCS mirror database.

    Every framework component should use this class instead of calling
    frappe.db.sql() directly.
    """

    DATABASE = "whmcs_mirror"

    @classmethod
    def get_row(cls, table, row_id):

        rows = frappe.db.sql(
            f"""
            SELECT *
            FROM {cls.DATABASE}.{table}
            WHERE id=%s
            """,
            (row_id,),
            as_dict=True,
        )

        if not rows:
            return None

        return rows[0]

    @classmethod
    def get_rows(cls, table, where="", values=()):

        sql = f"SELECT * FROM {cls.DATABASE}.{table}"

        if where:
            sql += f" WHERE {where}"

        return frappe.db.sql(
            sql,
            values,
            as_dict=True,
        )

    @classmethod
    def exists(cls, table, row_id):

        return cls.get_row(
            table,
            row_id,
        ) is not None
