from .models import (
    PaymentReconciliationCandidate,
    PaymentReconciliationResult,
)


class PaymentReconciliationValidator:

    def validate(
        self,
        candidate: PaymentReconciliationCandidate,
    ) -> PaymentReconciliationResult:

        result = PaymentReconciliationResult(total=1)

        #
        # Payment Entry
        #
        if not candidate.payment_entry:
            result.failed += 1
            result.missing_payment_entry += 1
            return result

        #
        # Expected Sales Invoice
        #
        if not candidate.expected_sales_invoice:
            result.failed += 1
            result.missing_sales_invoice += 1
            return result

        #
        # Allocation Validation
        #
        if (
            candidate.allocated_sales_invoice
            != candidate.expected_sales_invoice
        ):
            result.failed += 1
            result.missing_allocation += 1
            return result

        #
        # Amount Validation
        #
        if abs(candidate.whmcs_amount - candidate.paid_amount) > 0.01:
            result.failed += 1
            result.amount_mismatch += 1
            return result

        #
        # PASS
        #
        result.passed += 1

        return result
