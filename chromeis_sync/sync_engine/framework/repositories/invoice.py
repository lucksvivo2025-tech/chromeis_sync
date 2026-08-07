from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository):

    doctype = "Sales Invoice"
    whmcs_field = "whmcs_invoice_id"

    default_fields = [
        "name",
        "customer",
        "status",
        "outstanding_amount",
        "grand_total",
        "posting_date",
        "docstatus",
        "debit_to",
        "whmcs_invoice_id",
    ]

    @classmethod
    def find_by_whmcs_invoice_id(cls, invoice_id):
        return cls.find(invoice_id)
