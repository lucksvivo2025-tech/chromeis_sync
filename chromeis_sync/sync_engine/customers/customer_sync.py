from chromeis_sync.sync_engine.logger import SyncLogger
from chromeis_sync.sync_engine.config import SyncConfig

from chromeis_sync.sync_engine.customers.customer_planner import CustomerPlanner
from chromeis_sync.sync_engine.customers.customer_transaction import CustomerTransaction


class CustomerSync:

    def run(self):

        SyncLogger.info("Customer Sync Started")

        customer_ids = CustomerPlanner.pending(
            SyncConfig.BATCH_SIZE
        )

        SyncLogger.info(
            f"{len(customer_ids)} customers pending"
        )

        success = 0
        failed = 0

        for userid in customer_ids:

            try:
                CustomerTransaction(userid).execute()
                success += 1

            except Exception as e:

                failed += 1

                SyncLogger.error(
                    f"Customer {userid}: {e}"
                )

        SyncLogger.info(
            f"Customers Synced: {success}"
        )

        SyncLogger.info(
            f"Customers Failed: {failed}"
        )

        SyncLogger.info("Customer Sync Finished")
