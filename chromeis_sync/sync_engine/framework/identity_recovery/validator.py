from chromeis_sync.sync_engine.framework.identity_recovery.entities.invoice_item import (
    InvoiceItemRecoveryAnalyzer,
)


class IdentityRecoveryValidator:

    @staticmethod
    def invoice(invoice_id):

        result = InvoiceItemRecoveryAnalyzer.analyze(invoice_id)

        if result.status == "ERP_MISSING":
            return {
                "invoice": invoice_id,
                "valid": False,
                "status": result.status,
                "reason": "ERP Invoice not found",
            }

        recovered = result.matched_items
        failed = result.unmatched_items

        return {
            "invoice": invoice_id,
            "erp_invoice": result.erp_invoice,
            "status": result.status,
            "total_whmcs_items": result.total_whmcs_items,
            "supported_items": result.supported_items,
            "unsupported_items": result.unsupported_items,
            "matched_items": result.matched_items,
            "unmatched_items": result.unmatched_items,
            "recovered": recovered,
            "failed": failed,
            "success_rate": (
                round((recovered / result.supported_items) * 100, 2)
                if result.supported_items
                else 0
            ),
            "matches": result.matches,
            "valid": result.status == "RECOVERABLE",
        }
