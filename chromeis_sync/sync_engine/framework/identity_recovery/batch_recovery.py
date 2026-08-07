import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)


class BatchIdentityRecovery:

    @staticmethod
    def run(limit=None, commit=False):

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["!=", ""],
            },
            fields=[
                "name",
                "whmcs_invoice_id",
            ],
            order_by="creation asc",
            limit_page_length=limit or 100000,
        )

        summary = {
            "total": 0,
            "recoverable": 0,
            "recovered": 0,
            "partial": 0,
            "unsupported": 0,
            "empty": 0,
            "erp_missing": 0,
            "failed": 0,
            "details": [],
        }

        for invoice in invoices:

            invoice_id = int(invoice["whmcs_invoice_id"])

            result = IdentityRecoveryEngine.invoice(
                invoice_id,
                commit=commit,
            )

            analysis = result["analysis"]

            summary["total"] += 1

            if analysis.status == "RECOVERABLE":

                summary["recoverable"] += 1

                if commit and result["recovery"]:
                    summary["recovered"] += 1

            elif analysis.status == "PARTIAL":
                summary["partial"] += 1

            elif analysis.status == "UNSUPPORTED":
                summary["unsupported"] += 1

            elif analysis.status == "EMPTY":
                summary["empty"] += 1

            elif analysis.status == "ERP_MISSING":
                summary["erp_missing"] += 1

            else:
                summary["failed"] += 1

            summary["details"].append(
                {
                    "erp_invoice": invoice["name"],
                    "whmcs_invoice_id": invoice_id,
                    "status": analysis.status,
                    "supported": analysis.supported_items,
                    "matched": analysis.matched_items,
                    "unmatched": analysis.unmatched_items,
                    "unsupported": analysis.unsupported_items,
                }
            )

        return summary
