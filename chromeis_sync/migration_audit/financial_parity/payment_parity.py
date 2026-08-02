import frappe


class PaymentParity:

    def execute(self):

        print()
        print("=" * 80)
        print("PAYMENT PARITY")
        print("=" * 80)

        # WHMCS payments that were imported into ERP
        whmcs = frappe.db.sql("""
            SELECT
                COUNT(*) AS total,
                ROUND(SUM(a.amountin),2) AS amount
            FROM whmcs_mirror.tblaccounts a
            JOIN `tabPayment Entry` pe
                ON pe.custom_whmcs_txn_id = CAST(a.id AS CHAR)
            WHERE
                pe.docstatus = 1
        """, as_dict=True)[0]

        # ERP imported payments
        erp = frappe.db.sql("""
            SELECT
                COUNT(*) AS total,
                ROUND(SUM(paid_amount),2) AS amount
            FROM `tabPayment Entry`
            WHERE
                docstatus = 1
                AND custom_whmcs_txn_id IS NOT NULL
                AND custom_whmcs_txn_id <> ''
        """, as_dict=True)[0]

        # WHMCS payments not imported
        missing = frappe.db.sql("""
            SELECT
                COUNT(*) AS total
            FROM whmcs_mirror.tblaccounts a
            WHERE
                a.amountin > 0
                AND NOT EXISTS (
                    SELECT 1
                    FROM `tabPayment Entry` pe
                    WHERE
                        pe.custom_whmcs_txn_id = CAST(a.id AS CHAR)
                )
        """, as_dict=True)[0]

        print(f"Matched WHMCS Payments : {whmcs.total}")
        print(f"ERP Imported Payments  : {erp.total}")
        print()

        print(f"WHMCS Amount : {float(whmcs.amount or 0):,.2f}")
        print(f"ERP Amount   : {float(erp.amount or 0):,.2f}")
        print()

        print(f"Unmatched WHMCS Payments : {missing.total}")
        print()

        if (
            int(whmcs.total) == int(erp.total)
            and round(float(whmcs.amount or 0), 2)
                == round(float(erp.amount or 0), 2)
        ):
            print("PASS")
        else:
            print("FAIL")
