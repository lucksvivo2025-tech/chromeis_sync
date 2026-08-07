from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class InvoiceItemRepository(BaseRepository):

    doctype = "Sales Invoice Item"

    whmcs_field = "custom_whmcs_service_id"

    default_fields = [
        "parent",
        "idx",
        "item_code",
        "item_name",
        "custom_whmcs_service_id",
        "custom_whmcs_domain_id",
        "custom_whmcs_addon_id",
        "custom_whmcs_config_id",
    ]

    @classmethod
    def find_by_whmcs_service_id(cls, service_id):
        return cls.find(service_id)

    @classmethod
    def find_by_whmcs_domain_id(cls, domain_id):
        return cls.find_by_field(
            "custom_whmcs_domain_id",
            domain_id,
        )

    @classmethod
    def find_by_whmcs_addon_id(cls, addon_id):
        return cls.find_by_field(
            "custom_whmcs_addon_id",
            addon_id,
        )

    @classmethod
    def find_by_whmcs_config_id(cls, config_id):
        return cls.find_by_field(
            "custom_whmcs_config_id",
            config_id,
        )
