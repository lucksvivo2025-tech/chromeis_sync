from chromeis_sync.sync_engine.framework.identity.service import IdentityService

from chromeis_sync.sync_engine.framework.models.relationship_result import (
    RelationshipResult,
)


class InvoiceRelationshipResolver:
    """
    Builds the ERP relationship graph for a WHMCS Invoice.

    Version 1:
        Invoice only.

    Future versions will attach:
        - Customer
        - Invoice Items
        - Products
        - Payments
        - Credits
        - Services
        - Domains
        - Addons
    """

    @staticmethod
    def resolve(invoice_id):

        invoice = IdentityService.resolve_invoice(invoice_id)

        result = RelationshipResult(
            root_type="Invoice",
            root_document=invoice.document_name,
        )

        result.metadata = {
            "whmcs_invoice_id": str(invoice_id),
            "erp_invoice": invoice.document_name,
            "identity_status": str(invoice.status),
        }

        if invoice.found:

            customer_name = invoice.data.get("customer")

            if customer_name:

                # NOTE:
                # This will be improved later. For now we're only proving
                # the relationship pipeline.

                result.customer = customer_name

        return result
