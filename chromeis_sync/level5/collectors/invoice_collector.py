import frappe

from chromeis_sync.level5.api.client import Level5WHMCSClient


class InvoiceCollector:

    @staticmethod
    def collect(whmcs_invoice_id, erp_invoice_id):

        api = Level5WHMCSClient()

        whmcs = api.get_invoice(whmcs_invoice_id)

        mirror = frappe.db.sql("""
            SELECT *
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
            LIMIT 1
        """, (whmcs_invoice_id,), as_dict=True)

        if not mirror:
            mirror = None
        else:
            mirror = mirror[0]

        erp = frappe.get_doc(
            "Sales Invoice",
            erp_invoice_id,
        )

        return {
            "whmcs_id": str(whmcs_invoice_id),
            "erp_id": erp_invoice_id,
            "api": whmcs,
            "mirror": mirror,
            "erp": {
                "name": erp.name,
                "customer": erp.customer,
                "posting_date": str(erp.posting_date),
                "due_date": str(erp.due_date),
                "currency": erp.currency,
                "conversion_rate": erp.conversion_rate,
                "total": float(erp.total or 0),
                "net_total": float(erp.net_total or 0),
                "grand_total": float(erp.grand_total or 0),
                "outstanding_amount": float(
                    erp.outstanding_amount or 0
                ),
                "discount_amount": float(
                    erp.discount_amount or 0
                ),
                "status": erp.status,
                "docstatus": erp.docstatus,
                "items": [
                    {
                        "item_code": i.item_code,
                        "description": i.description,
                        "qty": float(i.qty or 0),
                        "rate": float(i.rate or 0),
                        "amount": float(i.amount or 0),
                        "net_amount": float(i.net_amount or 0),
                    }
                    for i in erp.items
                ],
                "taxes": [
                    {
                        "account_head": t.account_head,
                        "rate": float(t.rate or 0),
                        "tax_amount": float(
                            t.tax_amount or 0
                        ),
                        "total": float(t.total or 0),
                    }
                    for t in erp.taxes
                ],
            },
        }
