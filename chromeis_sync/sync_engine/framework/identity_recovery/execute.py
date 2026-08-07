import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)


class IdentityRecoveryExecutor:

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

        result = {
            "total": len(invoices),
            "recoverable": 0,
            "processed": 0,
            "updated_rows": 0,
            "skipped": 0,
            "failed": 0,
            "details": [],
        }

        for invoice in invoices:

            invoice_id = int(invoice.whmcs_invoice_id)

            try:

                engine = IdentityRecoveryEngine.invoice(
                    invoice_id,
                    commit=commit,
                )

                analysis = engine["analysis"]

                if analysis.status != "RECOVERABLE":

                    result["skipped"] += 1

                    result["details"].append(
                        {
                            "invoice": invoice_id,
                            "erp_invoice": analysis.erp_invoice,
                            "status": analysis.status,
                            "updated": 0,
                        }
                    )

                    continue

                result["recoverable"] += 1

                recovery = engine["recovery"]

                updated = (
                    recovery["updated_count"]
                    if recovery
                    else 0
                )

                result["processed"] += 1
                result["updated_rows"] += updated

                result["details"].append(
                    {
                        "invoice": invoice_id,
                        "erp_invoice": analysis.erp_invoice,
                        "status": analysis.status,
                        "updated": updated,
                    }
                )

            except Exception as e:

                result["failed"] += 1

                result["details"].append(
                    {
                        "invoice": invoice_id,
                        "status": "FAILED",
                        "error": str(e),
                    }
                )

        if commit:
            frappe.db.commit()

        return result
