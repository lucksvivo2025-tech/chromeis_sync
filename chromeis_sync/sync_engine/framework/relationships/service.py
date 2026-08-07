from chromeis_sync.sync_engine.framework.relationships.entities.invoice import (
    InvoiceRelationshipResolver,
)


class RelationshipService:

    @staticmethod
    def resolve_invoice(invoice_id):
        return InvoiceRelationshipResolver.resolve(invoice_id)
