from .planner import PaymentReconciliationPlanner
from .validator import PaymentReconciliationValidator
from .models import PaymentReconciliationResult


class PaymentReconciliationReport:

    def execute(self):

        planner = PaymentReconciliationPlanner()
        validator = PaymentReconciliationValidator()

        candidates = planner.execute()

        summary = PaymentReconciliationResult()

        summary.total = len(candidates)

        for candidate in candidates:

            result = validator.validate(candidate)

            summary.passed += result.passed
            summary.failed += result.failed

            summary.missing_payment_entry += result.missing_payment_entry
            summary.missing_sales_invoice += result.missing_sales_invoice

            summary.customer_mismatch += result.customer_mismatch
            summary.amount_mismatch += result.amount_mismatch

            summary.missing_allocation += result.missing_allocation

            summary.refunds += result.refunds

            summary.cancelled_payment += result.cancelled_payment
            summary.cancelled_invoice += result.cancelled_invoice

            summary.warnings += result.warnings

        print()
        print("=" * 80)
        print("PAYMENT RECONCILIATION")
        print("=" * 80)

        print(f"Total Payments          : {summary.total}")
        print(f"Passed                  : {summary.passed}")
        print(f"Failed                  : {summary.failed}")

        print()

        print(f"Missing Payment Entry   : {summary.missing_payment_entry}")
        print(f"Missing Sales Invoice   : {summary.missing_sales_invoice}")
        print(f"Missing Allocation      : {summary.missing_allocation}")
        print(f"Customer Mismatch       : {summary.customer_mismatch}")
        print(f"Amount Mismatch         : {summary.amount_mismatch}")

        print()

        print(f"Refunds                 : {summary.refunds}")
        print(f"Cancelled Payments      : {summary.cancelled_payment}")
        print(f"Cancelled Invoices      : {summary.cancelled_invoice}")
        print(f"Warnings                : {summary.warnings}")

        print("=" * 80)

        return summary
