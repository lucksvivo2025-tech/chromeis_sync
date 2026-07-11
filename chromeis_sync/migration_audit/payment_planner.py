import frappe


class PaymentPlanner:

    def pending_payments(self, limit=None):

        sql = """
        SELECT
            a.id
        FROM whmcs_mirror.tblaccounts a

        LEFT JOIN `tabPayment Entry` pe
            ON pe.custom_whmcs_txn_id = CAST(a.id AS CHAR)
            AND pe.docstatus != 2

        WHERE pe.name IS NULL

          AND IFNULL(a.amountin,0) > 0

          AND NOT (
                IFNULL(a.invoiceid,0) = 0
            AND IFNULL(a.gateway,'') = ''
            AND IFNULL(a.transid,'') = ''
            AND LOWER(IFNULL(a.description,'')) LIKE 'credit from refund%%'
          )

        ORDER BY a.id
        """

        if limit:
            sql += f" LIMIT {int(limit)}"

        rows = frappe.db.sql(sql, as_dict=True)

        return [row.id for row in rows]
