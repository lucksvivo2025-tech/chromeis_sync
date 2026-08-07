import frappe


class MergeDetector:

    @staticmethod
    def analyze(invoice_id):

        erp_invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(invoice_id),
            },
            "name",
        )

        if not erp_invoice:
            return None

        whmcs = frappe.db.sql(
            """
            SELECT
                amount,
                type,
                description
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            """,
            (invoice_id,),
            as_dict=True,
        )

        erp = frappe.db.sql(
            """
            SELECT
                amount
            FROM `tabSales Invoice Item`
            WHERE parent=%s
            """,
            (erp_invoice,),
            as_dict=True,
        )

        if not whmcs or not erp:
            return None

        supported = 0

        for row in whmcs:

            t = (row.get("type") or "").strip()

            if t in (
                "Hosting",
                "PromoHosting",
                "Domain",
                "DomainRegister",
                "DomainTransfer",
                "Addon",
            ):
                supported += 1
                continue

            if not t:
                supported += 1

        if supported <= len(erp):
            return None

        whmcs_total = round(
            sum(float(x["amount"]) for x in whmcs),
            2,
        )

        erp_total = round(
            sum(float(x["amount"]) for x in erp),
            2,
        )

        if whmcs_total != erp_total:
            return None

        return {
            "invoice": invoice_id,
            "erp_invoice": erp_invoice,
            "merged": True,
            "supported_items": supported,
            "erp_rows": len(erp),
            "whmcs_total": whmcs_total,
            "erp_total": erp_total,
        }
