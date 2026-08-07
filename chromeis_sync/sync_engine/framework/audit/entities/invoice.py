from chromeis_sync.sync_engine.framework.models.audit_result import AuditResult
from chromeis_sync.sync_engine.framework.identity.service import IdentityService


class InvoiceAudit:

    """
    Invoice Audit

    Validates a WHMCS invoice against its ERP mirror.
    """

    @staticmethod
    def audit(invoice_id):

        result = AuditResult(
            entity_type="Invoice",
            entity_id=str(invoice_id),
        )

        invoice = IdentityService.resolve_invoice(invoice_id)

        result.metadata = {
            "whmcs_invoice_id": str(invoice_id),
        }

        if not invoice.found:

            result.errors.append(
                "Invoice missing from ERP mirror."
            )

            return result

        result.metadata["erp_invoice"] = invoice.document_name

        result.metadata["identity_status"] = str(invoice.status)

        return result
