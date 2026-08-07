from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class OrderRepository(BaseRepository):

    doctype = "Sales Order"

    whmcs_field = "custom_whmcs_order_id"

    default_fields = [
        "name",
        "customer",
        "transaction_date",
        "status",
        "docstatus",
        "custom_whmcs_order_id",
    ]

    @classmethod
    def find_by_whmcs_order_id(cls, order_id):
        return cls.find(order_id)
