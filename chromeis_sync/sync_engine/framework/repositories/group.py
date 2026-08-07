from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class GroupRepository(BaseRepository):

    doctype = "Item Group"

    whmcs_field = "custom_whmcs_group_id"

    default_fields = [
        "name",
        "custom_whmcs_group_id",
    ]

    @classmethod
    def find_by_whmcs_group_id(cls, group_id):
        return cls.find(group_id)
