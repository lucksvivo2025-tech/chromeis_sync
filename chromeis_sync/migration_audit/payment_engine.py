import traceback

from chromeis_sync.migration_audit.payment_planner import PaymentPlanner
from chromeis_sync.migration_audit.payment_transaction import PaymentTransaction


class PaymentEngine:

    def run(self, limit=None):

        planner = PaymentPlanner()

        payment_ids = planner.pending_payments(limit)

        print()
        print("=" * 70)
        print(f"Payments Found : {len(payment_ids)}")
        print("=" * 70)

        success = 0
        failed = 0

        for payment_id in payment_ids:

            try:

                PaymentTransaction(payment_id).execute()

                success += 1

            except Exception:

                failed += 1

                traceback.print_exc()

        print()
        print("=" * 70)
        print("PAYMENT MIGRATION COMPLETE")
        print("=" * 70)
        print(f"Success : {success}")
        print(f"Failed  : {failed}")

        return {
            "success": success,
            "failed": failed,
        }
