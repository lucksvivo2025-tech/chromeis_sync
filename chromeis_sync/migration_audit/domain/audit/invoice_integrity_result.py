from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class InvoiceIntegrityResult:
    """
    Result of validating the internal financial integrity
    of a WHMCS invoice.
    """

    invoice_id: int

    status: str

    header_total: Decimal

    item_total: Decimal

    difference: Decimal

    item_count: int

    @property
    def valid(self) -> bool:
        """
        True when the invoice header exactly matches
        the sum of its invoice items.
        """
        return self.status == "EXACT_MATCH"
