import frappe


class GLParity:

    def execute(self):

        print()
        print("=" * 80)
        print("GENERAL LEDGER PARITY")
        print("=" * 80)

        gl = frappe.db.sql("""
            SELECT
                ROUND(SUM(debit),2) AS debit,
                ROUND(SUM(credit),2) AS credit,
                ROUND(SUM(debit-credit),2) AS balance
            FROM `tabGL Entry`
            WHERE is_cancelled = 0
        """, as_dict=True)[0]

        print(f"Debit  : {gl.debit:,.2f}")
        print(f"Credit : {gl.credit:,.2f}")
        print(f"Balance: {gl.balance:,.2f}")

        if abs(gl.balance) < 0.01:
            print()
            print("PASS")
        else:
            print()
            print("FAIL")
