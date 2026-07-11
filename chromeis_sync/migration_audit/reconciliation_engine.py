import frappe


class ReconciliationEngine:

    def run(self):

        print()
        print("=" * 70)
        print("FINAL MIGRATION RECONCILIATION")
        print("=" * 70)

        # --------------------------------------------------
        # Sales Invoices
        # --------------------------------------------------

        whmcs_invoices = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblinvoices
            WHERE status <> 'Draft'
        """)[0][0]

        erp_invoices = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabSales Invoice`
            WHERE whmcs_invoice_id IS NOT NULL
        """)[0][0]

        print()
        print("Sales Invoices")
        print("----------------------------")
        print(f"WHMCS : {whmcs_invoices}")
        print(f"ERP   : {erp_invoices}")
        print(f"Diff  : {whmcs_invoices - erp_invoices}")

        # --------------------------------------------------
        # Payments
        # --------------------------------------------------

        whmcs_payments = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblaccounts
            WHERE id NOT IN (
                SELECT id
                FROM whmcs_mirror.tblaccounts
                WHERE amountout > 0
                   OR description LIKE 'Refund%'
                   OR description LIKE 'Credit from Refund%'
            )
        """)[0][0]

        erp_payments = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabPayment Entry`
            WHERE custom_whmcs_txn_id IS NOT NULL
              AND docstatus != 2
        """)[0][0]

        print()
        print("Payments")
        print("----------------------------")
        print(f"WHMCS : {whmcs_payments}")
        print(f"ERP   : {erp_payments}")
        print(f"Diff  : {whmcs_payments - erp_payments}")

        # --------------------------------------------------
        # Excluded Refunds
        # --------------------------------------------------

        excluded = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblaccounts
            WHERE amountout > 0
               OR description LIKE 'Refund%'
               OR description LIKE 'Credit from Refund%'
        """)[0][0]

        print()
        print("Excluded Refund/Credit Records")
        print("----------------------------")
        print(excluded)

        # --------------------------------------------------
        # Duplicate Payments
        # --------------------------------------------------

        duplicates = frappe.db.sql("""
            SELECT COUNT(*)
            FROM (
                SELECT custom_whmcs_txn_id
                FROM `tabPayment Entry`
                WHERE custom_whmcs_txn_id IS NOT NULL
                GROUP BY custom_whmcs_txn_id
                HAVING COUNT(*) > 1
            ) x
        """)[0][0]

        print()
        print("Duplicate Payment Entries")
        print("----------------------------")
        print(duplicates)

        # --------------------------------------------------
        # Missing GL Entries
        # --------------------------------------------------

        missing_gl = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabPayment Entry` pe
            LEFT JOIN `tabGL Entry` gl
                ON gl.voucher_no = pe.name
            WHERE pe.custom_whmcs_txn_id IS NOT NULL
            GROUP BY pe.name
            HAVING COUNT(gl.name)=0
        """)

        missing_gl_count = len(missing_gl)

        print()
        print("Payment Entries Without GL")
        print("----------------------------")
        print(missing_gl_count)

        print()
        print("=" * 70)
        print("RECONCILIATION COMPLETE")
        print("=" * 70)

        return {
            "whmcs_invoices": whmcs_invoices,
            "erp_invoices": erp_invoices,
            "whmcs_payments": whmcs_payments,
            "erp_payments": erp_payments,
            "excluded_refunds": excluded,
            "duplicate_payments": duplicates,
            "missing_gl": missing_gl_count,
        }
