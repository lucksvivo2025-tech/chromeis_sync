import frappe


class InvoicePlanner:

    @staticmethod
    def pending(limit=100):

        rows = frappe.db.sql(
            """
            SELECT
                i.id
            FROM whmcs_mirror.tblinvoices i

            LEFT JOIN `tabSales Invoice` si
                ON si.whmcs_invoice_id = CAST(i.id AS CHAR)

            WHERE
                si.name IS NULL
                AND EXISTS (
                    SELECT 1
                    FROM whmcs_mirror.tblinvoiceitems it
                    WHERE it.invoiceid = i.id
                )

            ORDER BY i.id

            LIMIT %s
            """,
            (limit,),
        )

        return [r[0] for r in rows]
