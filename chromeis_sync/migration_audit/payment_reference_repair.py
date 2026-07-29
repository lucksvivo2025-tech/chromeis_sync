import frappe


class PaymentReferenceRepair:

    def run(self):
        candidates = self.get_candidates()

        duplicate_txn = frappe.db.sql("""
            SELECT custom_whmcs_txn_id
            FROM `tabPayment Entry`
            WHERE custom_whmcs_txn_id IS NOT NULL
            GROUP BY custom_whmcs_txn_id
            HAVING COUNT(*) > 1
        """)

        duplicate_invoice = frappe.db.sql("""
            SELECT ta.invoiceid
            FROM `tabPayment Entry` pe
            JOIN whmcs_mirror.tblaccounts ta
                ON ta.id = CAST(pe.custom_whmcs_txn_id AS UNSIGNED)
            GROUP BY ta.invoiceid
            HAVING COUNT(*) > 1
        """)

        stats = {
            "paid": 0,
            "partial": 0,
            "unpaid": 0,
            "overpayment": 0,
        }

        for row in candidates:

            outstanding = float(row.outstanding_amount)
            total = float(row.grand_total)
            payment = float(row.amountin)

            if abs(outstanding) < 0.01:
                stats["paid"] += 1
            elif abs(outstanding - total) < 0.01:
                stats["unpaid"] += 1
            else:
                stats["partial"] += 1

            if payment > total + 0.01:
                stats["overpayment"] += 1

        print("=" * 80)
        print(f"Broken Payment Entries           : {len(candidates)}")
        print(f"Duplicate WHMCS Transactions     : {len(duplicate_txn)}")
        print(f"Invoices with Multiple Payments  : {len(duplicate_invoice)}")
        print("=" * 80)

        print()
        print("SUMMARY")
        print("-" * 80)

        for key, value in stats.items():
            print(f"{key:15}: {value}")

    def get_candidates(self):

        return frappe.db.sql("""
            SELECT
                pe.name,
                pe.party,
                pe.custom_whmcs_txn_id,
                ta.invoiceid,
                ta.amountin,
                si.name AS sales_invoice,
                si.customer,
                si.currency,
                si.grand_total,
                si.outstanding_amount
            FROM `tabPayment Entry` pe
            JOIN whmcs_mirror.tblaccounts ta
                ON ta.id = CAST(pe.custom_whmcs_txn_id AS UNSIGNED)
            JOIN `tabSales Invoice` si
                ON CAST(si.whmcs_invoice_id AS UNSIGNED) = ta.invoiceid
            WHERE pe.docstatus = 1
              AND NOT EXISTS (
                    SELECT 1
                    FROM `tabPayment Entry Reference`
                    WHERE parent = pe.name
              )
            ORDER BY pe.name
        """, as_dict=True)


def execute():
    PaymentReferenceRepair().run()
