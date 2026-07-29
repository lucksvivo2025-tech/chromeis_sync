from __future__ import annotations

from decimal import Decimal

from chromeis_sync.migration_audit.domain.audit.invoice_integrity_result import (
    InvoiceIntegrityResult,
)
from chromeis_sync.migration_audit.domain.models.whmcs import (
    WHMCSInvoice,
)


class InvoiceIntegrityValidator:
    """
    Validates the internal financial integrity of a WHMCS invoice.

    This validator only checks WHMCS data.

    It does NOT:
        - compare against ERP
        - perform SQL queries
        - repair data

    Responsibility:
        Header Total == Sum(Invoice Items)
    """

    def validate(
        self,
        invoice: WHMCSInvoice,
    ) -> InvoiceIntegrityResult:

        item_total = sum(
            (item.amount for item in invoice.items),
            Decimal("0.00"),
        )

        header_total = invoice.header.total

        difference = header_total - item_total

        if difference == Decimal("0.00"):
            status = "EXACT_MATCH"

        elif difference > 0:
            status = "HEADER_GREATER_THAN_ITEMS"

        else:
            status = "ITEMS_GREATER_THAN_HEADER"

        return InvoiceIntegrityResult(
            invoice_id=invoice.header.invoice_id,
            status=status,
            header_total=header_total,
            item_total=item_total,
            difference=difference,
            item_count=len(invoice.items),
        )
