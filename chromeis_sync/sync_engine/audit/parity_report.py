import frappe


class ParityReport:

    @staticmethod
    def customers():

        whmcs = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblclients
        """)[0][0]

        erp = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabCustomer`
            WHERE
                custom_whmcs_user_id IS NOT NULL
                AND custom_whmcs_user_id != ''
        """)[0][0]

        return {
            "module": "Customers",
            "whmcs": whmcs,
            "erp": erp,
            "difference": whmcs - erp,
            "status": "PASS" if abs(whmcs - erp) <= 1 else "FAIL",
        }

    @staticmethod
    def invoices():

        whmcs = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblinvoices w
            WHERE
                w.status = 'Paid'
                AND EXISTS (
                    SELECT 1
                    FROM whmcs_mirror.tblinvoiceitems i
                    WHERE i.invoiceid = w.id
                )
        """)[0][0]

        erp = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabSales Invoice`
            WHERE
                docstatus = 1
                AND whmcs_invoice_id IS NOT NULL
                AND whmcs_invoice_id IN (
                    SELECT CAST(id AS CHAR)
                    FROM whmcs_mirror.tblinvoices
                    WHERE status = 'Paid'
                )
        """)[0][0]

        return {
            "module": "Paid Invoices",
            "whmcs": whmcs,
            "erp": erp,
            "difference": whmcs - erp,
            "status": "PASS" if whmcs == erp else "FAIL",
        }

    @staticmethod
    def payments():

        whmcs = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblaccounts
        """)[0][0]

        skipped = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblaccounts
            WHERE
                amountin = 0
                OR invoiceid = 0
        """)[0][0]

        expected = whmcs - skipped

        erp = frappe.db.count(
            "Payment Entry",
            {
                "custom_whmcs_txn_id": ["is", "set"]
            },
        )

        return {
            "module": "Payments",
            "whmcs": expected,
            "erp": erp,
            "difference": expected - erp,
            "status": "PASS" if expected == erp else "FAIL",
        }

    @staticmethod
    def customer_credits():

        whmcs = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblcredit
        """)[0][0]

        erp = frappe.db.count(
            "Journal Entry",
            {
                "custom_whmcs_credit_id": ["is", "set"]
            },
        )

        skipped = frappe.db.sql("""
            SELECT COUNT(*)
            FROM whmcs_mirror.tblcredit c

            LEFT JOIN whmcs_mirror.tblinvoices w
                ON w.id = c.relid

            LEFT JOIN `tabSales Invoice` s
                ON s.whmcs_invoice_id = CAST(c.relid AS CHAR)

            WHERE
                c.amount = 0
                OR (c.relid > 0 AND w.id IS NULL)
                OR (c.relid > 0 AND s.name IS NULL)
                OR (s.docstatus = 2)
        """)[0][0]

        expected = whmcs - skipped

        return {
            "module": "Customer Credits",
            "whmcs": expected,
            "erp": erp,
            "difference": expected - erp,
            "status": "PASS" if abs(expected - erp) <= 3 else "FAIL",
        }

    @classmethod
    def run(cls):

        return [
            cls.customers(),
            cls.invoices(),
            cls.payments(),
            cls.customer_credits(),
        ]
