from chromeis_sync.sync_engine.logger import SyncLogger
from chromeis_sync.sync_engine.config import SyncConfig


class SyncManager:
    """
    Main orchestrator for WHMCS synchronization.
    """

    def run(self):

        SyncLogger.separator()
        SyncLogger.info("Starting WHMCS Synchronization")
        SyncLogger.separator()

        if SyncConfig.ENABLE_CUSTOMER_SYNC:
            self.sync_customers()

        if SyncConfig.ENABLE_SERVICE_SYNC:
            self.sync_services()

        if SyncConfig.ENABLE_INVOICE_SYNC:
            self.sync_invoices()

        if SyncConfig.ENABLE_PAYMENT_SYNC:
            self.sync_payments()

        SyncLogger.separator()
        SyncLogger.info("Synchronization Complete")
        SyncLogger.separator()

    def sync_customers(self):
        SyncLogger.info("Customer Sync Started")
        # CustomerSync().run()
        SyncLogger.info("Customer Sync Finished")

    def sync_services(self):
        SyncLogger.info("Service Sync Started")
        # ServiceSync().run()
        SyncLogger.info("Service Sync Finished")

    def sync_invoices(self):
        SyncLogger.info("Invoice Sync Started")
        # InvoiceSync().run()
        SyncLogger.info("Invoice Sync Finished")

    def sync_payments(self):
        SyncLogger.info("Payment Sync Started")
        # PaymentSync().run()
        SyncLogger.info("Payment Sync Finished")
