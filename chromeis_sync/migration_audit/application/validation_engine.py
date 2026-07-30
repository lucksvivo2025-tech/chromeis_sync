from __future__ import annotations

from chromeis_sync.migration_audit.domain.models.validation import (
    ValidationIssue,
    ValidationResult,
)
from chromeis_sync.migration_audit.validation.invoice_integrity_validator import (
    InvoiceIntegrityValidator,
)


class ValidationEngine:
    """
    Coordinates financial validation.

    It orchestrates validators but contains no validation logic.
    """

    def __init__(self):

        self.integrity_validator = InvoiceIntegrityValidator()

    def validate(
        self,
        invoice,
    ) -> ValidationResult:

        result = ValidationResult()

        integrity = self.integrity_validator.validate(invoice)

        if not integrity.valid:

            result.add(
                ValidationIssue(
                    component="Invoice Integrity",
                    field="Header Total",
                    expected=integrity.item_total,
                    actual=integrity.header_total,
                    message=integrity.status,
                )
            )

        return result
