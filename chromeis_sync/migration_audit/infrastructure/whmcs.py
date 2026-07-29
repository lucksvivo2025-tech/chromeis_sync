import frappe


class WHMCSDatabase:
    """
    Helper for executing queries against the WHMCS mirror database.
    """

    DATABASE = "whmcs_mirror"

    @classmethod
    def query(cls, sql: str, params: tuple = ()):
        sql = sql.replace("FROM tbl", f"FROM {cls.DATABASE}.tbl")
        sql = sql.replace("JOIN tbl", f"JOIN {cls.DATABASE}.tbl")
        sql = sql.replace("UPDATE tbl", f"UPDATE {cls.DATABASE}.tbl")
        sql = sql.replace("INTO tbl", f"INTO {cls.DATABASE}.tbl")

        return frappe.db.sql(
            sql,
            values=params,
            as_dict=True,
        )
