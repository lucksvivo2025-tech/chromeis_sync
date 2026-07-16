from chromeis_sync.sync_engine.logger import SyncLogger
from chromeis_sync.sync_engine.invoices.invoice_planner import InvoicePlanner
from chromeis_sync.sync_engine.invoices.invoice_transaction import InvoiceTransaction


class InvoiceSync:

    def run(self, limit=100):

        SyncLogger.info("Invoice Sync Started")

        pending = InvoicePlanner.pending(limit)

        SyncLogger.info(f"{len(pending)} invoices pending")

        success = 0
        failed = 0

        for invoice_id in pending:

            try:
                InvoiceTransaction(invoice_id).execute()
                success += 1

            except Exception as e:
                failed += 1
                SyncLogger.error(f"Invoice {invoice_id}: {e}")

        SyncLogger.info(f"Invoices Synced: {success}")
        SyncLogger.info(f"Invoices Failed: {failed}")
        SyncLogger.info("Invoice Sync Finished")
