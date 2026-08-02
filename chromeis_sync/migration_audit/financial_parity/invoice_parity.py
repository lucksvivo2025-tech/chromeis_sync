import frappe


class InvoiceParity:

    def execute(self):

        print()
        print("=" * 80)
        print("INVOICE PARITY")
        print("=" * 80)

        whmcs = frappe.db.sql("""
            SELECT
                COUNT(*) AS total,
                ROUND(SUM(total),2) AS amount
            FROM whmcs_mirror.tblinvoices
            WHERE
                status='Paid'
                AND total > 0
        """, as_dict=True)[0]

        erp = frappe.db.sql("""
            SELECT
                COUNT(*) AS total,
                ROUND(SUM(si.grand_total),2) AS amount
            FROM `tabSales Invoice` si
            JOIN whmcs_mirror.tblinvoices w
                ON CAST(w.id AS CHAR)=si.whmcs_invoice_id
            WHERE
                si.docstatus=1
                AND w.status='Paid'
                AND w.total>0
        """, as_dict=True)[0]

        missing = frappe.db.sql("""
            SELECT
                COUNT(*) AS total
            FROM whmcs_mirror.tblinvoices w
            WHERE
                w.status='Paid'
                AND w.total>0
                AND NOT EXISTS (
                    SELECT 1
                    FROM `tabSales Invoice` si
                    WHERE si.whmcs_invoice_id=CAST(w.id AS CHAR)
                )
        """, as_dict=True)[0]

        cancelled = frappe.db.sql("""
            SELECT
                COUNT(*) AS total
            FROM whmcs_mirror.tblinvoices w
            JOIN `tabSales Invoice` si
                ON si.whmcs_invoice_id=CAST(w.id AS CHAR)
            WHERE
                w.status='Paid'
                AND w.total>0
                AND si.docstatus=2
        """, as_dict=True)[0]

        duplicates = frappe.db.sql("""
            SELECT COUNT(*) AS total
            FROM (
                SELECT whmcs_invoice_id
                FROM `tabSales Invoice`
                WHERE
                    docstatus=1
                    AND whmcs_invoice_id IS NOT NULL
                GROUP BY whmcs_invoice_id
                HAVING COUNT(*)>1
            ) x
        """, as_dict=True)[0]

        print(f"WHMCS Paid Invoices : {whmcs.total}")
        print(f"ERP Paid Invoices   : {erp.total}")
        print()

        print(f"WHMCS Amount : {float(whmcs.amount or 0):,.2f}")
        print(f"ERP Amount   : {float(erp.amount or 0):,.2f}")
        print()

        print(f"Missing Invoices   : {missing.total}")
        print(f"Cancelled Invoices : {cancelled.total}")
        print(f"Duplicate IDs      : {duplicates.total}")
        print()

        if missing.total == 0 and duplicates.total == 0:
            print("PASS")
        else:
            print("FAIL")
