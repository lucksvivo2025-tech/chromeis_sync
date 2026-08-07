from chromeis_sync.sync_engine.framework.audit.entities.invoice import (
    InvoiceAudit,
)


class AuditEngine:

    @staticmethod
    def audit_invoice(invoice_id):
        return InvoiceAudit.audit(invoice_id)
