import frappe


class CustomerCreditParity:

    def execute(self):

        print()
        print("=" * 80)
        print("CUSTOMER CREDIT PARITY")
        print("=" * 80)

        whmcs = frappe.db.sql("""
            SELECT
                COUNT(*) AS customers,
                ROUND(SUM(credit),2) AS credit
            FROM whmcs_mirror.tblclients
            WHERE credit > 0
        """, as_dict=True)[0]

        print(f"WHMCS Customers with Credit : {whmcs.customers}")
        print(f"WHMCS Credit Total          : {float(whmcs.credit or 0):,.2f}")
