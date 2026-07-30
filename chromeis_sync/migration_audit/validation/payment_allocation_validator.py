from chromeis_sync.migration_audit.domain.models.validation import (
    ValidationIssue,
    ValidationSeverity,
)
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
    ) -> list[ValidationIssue]:

        issues: list[ValidationIssue] = []

        erp_payment = self.erp_provider.load_payment(payment.id)

        if not erp_payment:

            issues.append(
                ValidationIssue(
                    component="Payment Allocation",
                    field=f"Payment {payment.id}",
                    expected="ERP Payment Exists",
                    actual="Missing ERP Payment",
                    severity=ValidationSeverity.ERROR,
                    message="Missing ERP Payment",
                )
            )

            return issues

        references = self.erp_provider.load_references(
            erp_payment["name"]
        )

        if payment.invoice_id and not references:

            issues.append(
                ValidationIssue(
                    component="Payment Allocation",
                    field=f"Payment {payment.id}",
                    expected="Allocated",
                    actual="Unallocated",
                    severity=ValidationSeverity.ERROR,
                    message="Missing Allocation",
                )
            )

        return issues

    def validate(
        self,
        invoice: WHMCSInvoice,
    ) -> list[ValidationIssue]:

        payments = self.whmcs_provider.load_payments(
            invoice.header.invoice_id
        )

        issues: list[ValidationIssue] = []

        for payment in payments:
            issues.extend(
                self.validate_payment(payment)
            )

        return issues
