from chromeis_sync.sync_engine.identity_completion.invoice_item import (
    InvoiceItemIdentityReport,
)


class IdentityCompletionReport:

    @staticmethod
    def invoice_items():
        return InvoiceItemIdentityReport.run()
