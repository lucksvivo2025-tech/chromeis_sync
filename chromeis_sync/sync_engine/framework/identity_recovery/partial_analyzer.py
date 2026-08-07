import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)


class PartialInvoiceAnalyzer:

    @staticmethod
    def analyze(invoice_id):

        result = IdentityRecoveryEngine.invoice(
            invoice_id,
            commit=False,
        )

        analysis = result["analysis"]

        report = {
            "invoice": invoice_id,
            "erp_invoice": analysis.erp_invoice,
            "status": analysis.status,
            "issues": [],
        }

        if analysis.status != "PARTIAL":
            return report

        #
        # unsupported items
        #

        for item in analysis.unsupported:

            report["issues"].append(
                {
                    "type": "UNSUPPORTED",
                    "item_type": item.get("type") or "(blank)",
                    "description": item.get("description"),
                    "amount": item.get("amount"),
                }
            )

        #
        # unmatched supported items
        #

        whmcs_items = frappe.db.sql(
            """
            SELECT
                id,
                type,
                relid,
                description,
                amount
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
            """,
            (invoice_id,),
            as_dict=True,
        )

        matched_ids = {
            m["whmcs_invoice_item_id"]
            for m in analysis.matches
        }

        for item in whmcs_items:

            if item["id"] in matched_ids:
                continue

            report["issues"].append(
                {
                    "type": "UNMATCHED",
                    "item_type": item.get("type") or "(blank)",
                    "description": item.get("description"),
                    "amount": item.get("amount"),
                    "relid": item.get("relid"),
                }
            )

        return report
