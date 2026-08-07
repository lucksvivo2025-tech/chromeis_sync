import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.validator import (
    IdentityRecoveryValidator,
)


class BatchIdentityValidator:

    @staticmethod
    def run(limit=None):

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
            "valid": 0,
            "partial": 0,
            "failed": 0,
            "details": [],
        }

        for invoice in invoices:

            result = IdentityRecoveryValidator.invoice(
                int(invoice["whmcs_invoice_id"])
            )

            summary["total"] += 1

            if result.get("valid"):
                summary["valid"] += 1

            elif result.get("matches"):
                summary["partial"] += 1

            else:
                summary["failed"] += 1

            summary["details"].append(
                {
                    "erp_invoice": invoice["name"],
                    "whmcs_invoice_id": invoice["whmcs_invoice_id"],
                    "valid": result.get("valid"),
                    "recovered": result.get("recovered", 0),
                    "total_items": result.get("total_items", 0),
                    "success_rate": result.get("success_rate", 0),
                }
            )

        return summary
