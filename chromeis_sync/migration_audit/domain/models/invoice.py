from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from chromeis_sync.migration_audit.domain.enums.invoice_classification import (
    InvoiceClassification,
)


@dataclass
class Invoice:

    id: int

    userid: int

    status: str

    subtotal: Decimal

    credit: Decimal

    tax: Decimal

    total: Decimal

    classification: Optional[InvoiceClassification] = None

    @property
    def paid_by_credit(self):

        return (
            self.status == "Paid"
            and self.credit > 0
            and self.credit == self.subtotal
            and self.total == 0
        )

    @property
    def true_zero(self):

        return (
            self.subtotal == 0
            and self.credit == 0
            and self.total == 0
        )
