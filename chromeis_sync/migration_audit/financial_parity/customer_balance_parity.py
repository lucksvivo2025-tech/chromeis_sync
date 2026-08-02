import frappe


class CustomerBalanceParity:

    def execute(self):

        print()
        print("=" * 80)
        print("CUSTOMER BALANCE PARITY")
        print("=" * 80)

        result = frappe.db.sql("""
            SELECT
                COUNT(*) AS customers,
                ROUND(SUM(balance),2) AS balance
            FROM (
                SELECT
                    party,
                    SUM(debit-credit) AS balance
                FROM `tabGL Entry`
                WHERE
                    party_type='Customer'
                    AND is_cancelled=0
                GROUP BY party
            ) x
        """, as_dict=True)[0]

        print(f"Customers : {result.customers}")
        print(f"Balance   : {result.balance:,.2f}")
