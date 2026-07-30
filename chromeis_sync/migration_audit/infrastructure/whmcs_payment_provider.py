from __future__ import annotations

from decimal import Decimal
from typing import List

from chromeis_sync.migration_audit.domain.models.whmcs import WHMCSPayment
from chromeis_sync.migration_audit.infrastructure.whmcs import WHMCSDatabase


class WHMCSPaymentProvider:
    """Loads payment information from WHMCS."""

    def load_payments(
        self,
        invoice_id: int,
    ) -> List[WHMCSPayment]:

        rows = WHMCSDatabase.query(
            """
            SELECT
                id,
                userid,
                invoiceid,
                amountin,
                description,
                date
            FROM tblaccounts
            WHERE description = 'Invoice Payment'
              AND invoiceid = %s
            ORDER BY id
            """,
            (invoice_id,),
        )

        payments = []

        for row in rows:
            payments.append(
                WHMCSPayment(
                    id=row["id"],
                    invoice_id=row["invoiceid"],
                    user_id=row["userid"],
                    amount=Decimal(str(row["amountin"])),
                    payment_date=row["date"],
                    transaction_id=None,
                    gateway=None,
                    fees=Decimal("0.00"),
                    currency=None,
                    exchange_rate=None,
                    notes=row["description"],
                )
            )

        return payments
