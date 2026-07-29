import frappe
from copy import deepcopy


class SnapshotService:

    @staticmethod
    def create(invoice_name):

        si = frappe.get_doc(
            "Sales Invoice",
            invoice_name
        )

        return {
            "header": deepcopy(si.as_dict()),

            "items": [
                deepcopy(d.as_dict())
                for d in si.items
            ],

            "taxes": [
                deepcopy(d.as_dict())
                for d in si.taxes
            ],

            "payments": [
                deepcopy(d.as_dict())
                for d in si.payments
            ],

            "payment_schedule": [
                deepcopy(d.as_dict())
                for d in si.payment_schedule
            ],

            "sales_team": [
                deepcopy(d.as_dict())
                for d in si.sales_team
            ],

            "gl_entries": frappe.db.sql("""
                SELECT *
                FROM `tabGL Entry`
                WHERE voucher_no=%s
                  AND creation = (
                      SELECT MIN(creation)
                      FROM `tabGL Entry`
                      WHERE voucher_no=%s
                  )
                ORDER BY account
            """, (si.name, si.name), as_dict=True),

            "whmcs_items": frappe.db.sql("""
                SELECT *
                FROM whmcs_mirror.tblinvoiceitems
                WHERE invoiceid=%s
                ORDER BY id
            """, si.whmcs_invoice_id, as_dict=True)
        }
