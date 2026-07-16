from chromeis_sync.sync_engine.customer_credits.handlers.overpayment import (
    OverpaymentHandler,
)

from chromeis_sync.sync_engine.customer_credits.handlers.credit_applied import (
    CreditAppliedHandler,
)


class CustomerCreditRouter:

    @staticmethod
    def build(snapshot):

        description = (snapshot.get("description") or "").lower()

        if "credit applied" in description:
            return CreditAppliedHandler(snapshot).build()

        if "overpayment" in description:
            return OverpaymentHandler(snapshot).build()

        # Temporary fallback
        return OverpaymentHandler(snapshot).build()
