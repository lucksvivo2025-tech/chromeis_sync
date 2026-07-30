from chromeis_sync.migration_audit.domain.models.whmcs import (
    WHMCSInvoice,
    WHMCSPayment,
)
from chromeis_sync.migration_audit.infrastructure.erp_payment_provider import (
    ERPPaymentProvider,
)
from chromeis_sync.migration_audit.infrastructure.whmcs_payment_provider import (
    WHMCSPaymentProvider,
)


class PaymentAllocationValidator:

    def __init__(self):

        self.erp_provider = ERPPaymentProvider()
        self.whmcs_provider = WHMCSPaymentProvider()

    def validate_payment(
        self,
        payment: WHMCSPayment,
    ):

        result = {
            "whmcs_txn_id": payment.id,
            "invoice_id": payment.invoice_id,
            "amount": payment.amount,
            "status": "PASS",
            "reason": None,
        }

        erp_payment = self.erp_provider.load_payment(payment.id)

        if not erp_payment:
            result["status"] = "FAIL"
            result["reason"] = "Missing ERP Payment"
            return result

        references = self.erp_provider.load_references(
            erp_payment["name"]
        )

        if payment.invoice_id and not references:
            result["status"] = "FAIL"
            result["reason"] = "Missing Allocation"

        return result

    def validate(
        self,
        invoice: WHMCSInvoice,
    ):

        payments = self.whmcs_provider.load_payments(
            invoice.header.invoice_id
        )

        return [
            self.validate_payment(payment)
            for payment in payments
        ]
