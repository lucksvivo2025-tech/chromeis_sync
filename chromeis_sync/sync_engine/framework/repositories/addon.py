from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class AddonRepository(BaseRepository):

    doctype = "Sales Invoice Item"

    whmcs_field = "custom_whmcs_addon_id"

    default_fields = [
        "parent",
        "item_code",
        "item_name",
        "custom_whmcs_addon_id",
    ]

    @classmethod
    def find_by_whmcs_addon_id(cls, addon_id):
        return cls.find(addon_id)
