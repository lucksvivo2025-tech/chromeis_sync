from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class ProductRepository(BaseRepository):
    """
    Product Repository

    Canonical ERP repository for WHMCS Products.

    Source of Truth:
        custom_whmcs_product_id

    Legacy Fields:
        whmcs_product_id
        whmcs_pid
    """

    doctype = "Item"

    whmcs_field = "custom_whmcs_product_id"

    default_fields = [
        "name",
        "item_name",
        "item_group",
        "disabled",
        "custom_whmcs_product_id",
        "custom_whmcs_group_id",
        "whmcs_product_id",
        "whmcs_pid",
    ]

    @classmethod
    def find_by_whmcs_product_id(cls, product_id):
        return cls.find(product_id)

    @classmethod
    def find_by_legacy_product_id(cls, product_id):
        return cls.find_by_field(
            "whmcs_product_id",
            product_id,
        )

    @classmethod
    def find_by_pid(cls, pid):
        return cls.find_by_field(
            "whmcs_pid",
            pid,
        )
