import frappe

from chromeis_sync.migration_audit.transaction import InvoiceTransaction


class MigrationEngine:

    def __init__(self):
        self.manifest = []

    def generate_manifest(self):

        self.manifest = frappe.db.sql("""
            SELECT
                si.name,
                si.whmcs_invoice_id,
                si.customer,
                si.currency AS erp_currency,
                c.code AS target_currency,
                si.grand_total,
                COUNT(sii.name) AS item_count
            FROM `tabSales Invoice` si

            JOIN `tabSales Invoice Item` sii
                ON sii.parent = si.name

            JOIN whmcs_mirror.tblinvoices i
                ON CAST(i.id AS CHAR)=si.whmcs_invoice_id

            JOIN whmcs_mirror.tblclients cl
                ON cl.id=i.userid

            JOIN whmcs_mirror.tblcurrencies c
                ON c.id=cl.currency

            WHERE
                si.docstatus = 1
                AND si.currency != c.code

            GROUP BY si.name

            ORDER BY CAST(si.whmcs_invoice_id AS UNSIGNED)
        """, as_dict=True)

        print(f"Manifest contains {len(self.manifest)} invoices")

    def test_transaction(self, invoice_name):

        row = next(
            r for r in self.manifest
            if r.name == invoice_name
        )

        txn = InvoiceTransaction(
            invoice_name,
            row.target_currency
        )

        return txn.execute()

    def run(self):

        self.generate_manifest()

        print("\nEngine Ready")
