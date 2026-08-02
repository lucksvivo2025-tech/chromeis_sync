import frappe


class PaymentLedgerParity:

    def execute(self):

        print()
        print("=" * 80)
        print("PAYMENT LEDGER PARITY")
        print("=" * 80)

        submitted = frappe.db.sql("""
            SELECT COUNT(*) AS total
            FROM `tabPayment Entry`
            WHERE docstatus = 1
        """, as_dict=True)[0]

        missing = frappe.db.sql("""
            SELECT COUNT(*) AS total
            FROM `tabPayment Entry` pe
            WHERE
                pe.docstatus = 1
                AND NOT EXISTS (
                    SELECT 1
                    FROM `tabPayment Ledger Entry` ple
                    WHERE
                        ple.voucher_type='Payment Entry'
                        AND ple.voucher_no=pe.name
                )
        """, as_dict=True)[0]

        orphan = frappe.db.sql("""
            SELECT COUNT(*) AS total
            FROM `tabPayment Ledger Entry` ple
            LEFT JOIN `tabPayment Entry` pe
                ON pe.name = ple.voucher_no
            WHERE
                ple.voucher_type='Payment Entry'
                AND pe.name IS NULL
        """, as_dict=True)[0]

        cancelled = frappe.db.sql("""
            SELECT COUNT(*) AS total
            FROM `tabPayment Ledger Entry` ple
            JOIN `tabPayment Entry` pe
                ON pe.name = ple.voucher_no
            WHERE
                ple.voucher_type='Payment Entry'
                AND pe.docstatus = 2
        """, as_dict=True)[0]

        deleted = frappe.db.sql("""
            SELECT
                COUNT(DISTINCT voucher_no) AS total
            FROM `tabPayment Ledger Entry`
            WHERE
                voucher_type='Payment Entry'
                AND voucher_no LIKE 'ACC-PAY-%'
                AND voucher_no NOT IN (
                    SELECT name
                    FROM `tabPayment Entry`
                )
        """, as_dict=True)[0]

        print(f"Submitted Payment Entries : {submitted.total}")
        print(f"Missing Ledger Entries    : {missing.total}")
        print()

        print(f"Deleted Payment Entries   : {deleted.total}")
        print(f"Cancelled Payment Rows    : {cancelled.total}")
        print(f"Orphan Ledger Rows        : {orphan.total}")
        print()

        if missing.total == 0:
            print("PASS")
        else:
            print("FAIL")
