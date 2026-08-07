from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class PaymentRepository(BaseRepository):

    doctype = "Payment Entry"

    whmcs_field = "custom_whmcs_txn_id"

    default_fields = [
        "name",
        "party",
        "party_type",
        "paid_amount",
        "received_amount",
        "posting_date",
        "docstatus",
        "reference_no",
        "custom_whmcs_txn_id",
        "custom_whmcs_credit_id",
    ]

    @classmethod
    def find_by_whmcs_txn_id(cls, txn_id):
        return cls.find(txn_id)

    @classmethod
    def find_by_whmcs_credit_id(cls, credit_id):
        return cls.find_by_field(
            "custom_whmcs_credit_id",
            credit_id,
        )
