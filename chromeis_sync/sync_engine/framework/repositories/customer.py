from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class CustomerRepository(BaseRepository):

    doctype = "Customer"
    whmcs_field = "custom_whmcs_user_id"

    default_fields = [
        "name",
        "customer_name",
        "custom_whmcs_user_id",
        "custom_whmcs_client_id",
    ]

    @classmethod
    def find_by_whmcs_user_id(cls, user_id):
        return cls.find(user_id)

    @classmethod
    def find_by_whmcs_client_id(cls, client_id):
        return cls.find_by_field(
            "custom_whmcs_client_id",
            client_id,
        )
