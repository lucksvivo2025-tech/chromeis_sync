import frappe

from chromeis_sync.sync_engine.logger import SyncLogger
from chromeis_sync.sync_engine.customer_credits.customer_credit_transaction import (
    CustomerCreditTransaction,
)


class CustomerCreditSync:

    @staticmethod
    def pending(limit=100):

        existing = {
            str(x[0])
            for x in frappe.db.sql(
                """
                SELECT custom_whmcs_credit_id
                FROM `tabJournal Entry`
                WHERE custom_whmcs_credit_id IS NOT NULL
                """
            )
            if x[0]
        }

        credits = frappe.db.sql(
            """
            SELECT id
            FROM whmcs_mirror.tblcredit
            ORDER BY id
            """,
            as_dict=True,
        )

        pending = [
            row["id"]
            for row in credits
            if str(row["id"]) not in existing
        ]

        return pending[:limit]

    def run(self, limit=100):

        SyncLogger.info("Customer Credit Sync Started")

        pending = self.pending(limit)

        SyncLogger.info(f"{len(pending)} customer credits pending")

        created = 0
        skipped = 0
        failed = 0

        for credit_id in pending:

            try:

                journal = CustomerCreditTransaction(credit_id).execute()

                if journal:
                    created += 1
                else:
                    skipped += 1

            except Exception as e:

                failed += 1
                SyncLogger.error(f"Customer Credit {credit_id}: {e}")

        SyncLogger.info(f"Customer Credits Created : {created}")
        SyncLogger.info(f"Customer Credits Skipped : {skipped}")
        SyncLogger.info(f"Customer Credits Failed  : {failed}")
        SyncLogger.info("Customer Credit Sync Finished")
