import traceback

from chromeis_sync.migration_audit.missing_invoice_planner import (
    MissingInvoicePlanner,
)
from chromeis_sync.migration_audit.missing_invoice_transaction import (
    MissingInvoiceTransaction,
)


class MissingInvoiceEngine:

    def __init__(self, target_currency="USD"):

        self.target_currency = target_currency
        self.planner = MissingInvoicePlanner()

    def summary(self):

        self.planner.print_summary()

    def execute_one(self):

        plan = self.planner.plan()

        if not plan:
            print("Nothing to recover.")
            return None

        row = plan[0]

        return MissingInvoiceTransaction(
            int(row["whmcs_invoice_id"]),
            self.target_currency,
        ).execute()

    def execute(self, limit=None):

        plan = self.planner.plan()

        if limit:
            plan = plan[:limit]

        results = []

        for row in plan:

            print()
            print("#" * 70)
            print(
                f"Recovering WHMCS Invoice {row['whmcs_invoice_id']}"
            )

            try:

                result = MissingInvoiceTransaction(
                    int(row["whmcs_invoice_id"]),
                    self.target_currency,
                ).execute()

                results.append(result)

            except Exception:

                traceback.print_exc()

        print()
        print("=" * 60)
        print("Recovery Summary")
        print("=" * 60)
        print(f"Requested : {len(plan)}")
        print(f"Recovered : {len(results)}")
        print(f"Failed    : {len(plan)-len(results)}")
        print("=" * 60)

        return results
