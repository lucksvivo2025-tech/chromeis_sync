from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class CreditRepository(BaseRepository):

    doctype = "Journal Entry"

    whmcs_field = "custom_whmcs_credit_id"

    default_fields = [
        "name",
        "voucher_type",
        "posting_date",
        "docstatus",
        "custom_whmcs_credit_id",
    ]

    @classmethod
    def find_by_whmcs_credit_id(cls, credit_id):
        return cls.find(credit_id)
