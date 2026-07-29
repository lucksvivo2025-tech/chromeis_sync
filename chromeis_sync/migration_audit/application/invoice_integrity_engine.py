from __future__ import annotations

from chromeis_sync.migration_audit.domain.audit.invoice_integrity_result import (
    InvoiceIntegrityResult,
)
from chromeis_sync.migration_audit.infrastructure.providers.whmcs_provider import (
    WHMCSProvider,
)
from chromeis_sync.migration_audit.validation.invoice_integrity_validator import (
    InvoiceIntegrityValidator,
)


class InvoiceIntegrityEngine:
    """
    Application service responsible for validating the
    internal integrity of WHMCS invoices.

    Flow:

        WHMCSProvider
              │
              ▼
        WHMCSInvoice
              │
              ▼
        InvoiceIntegrityValidator
              │
              ▼
        InvoiceIntegrityResult
    """

    def __init__(self):

        self.provider = WHMCSProvider()
        self.validator = InvoiceIntegrityValidator()

    def validate(
        self,
        invoice_id: int,
    ) -> InvoiceIntegrityResult:
        """
        Validate a single WHMCS invoice.
        """

        invoice = self.provider.load_invoice(invoice_id)

        return self.validator.validate(invoice)

    def validate_many(
        self,
        invoice_ids: list[int],
    ) -> list[InvoiceIntegrityResult]:
        """
        Validate multiple WHMCS invoices.
        """

        results = []

        for invoice_id in invoice_ids:
            results.append(
                self.validate(invoice_id)
            )

        return results
