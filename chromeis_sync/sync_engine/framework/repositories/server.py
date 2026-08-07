from chromeis_sync.sync_engine.framework.repositories.base import (
    BaseRepository,
)


class ServerRepository(BaseRepository):

    doctype = "Server"

    whmcs_field = "whmcs_id"

    default_fields = [
        "name",
        "server_name",
        "ip_address",
        "provider",
        "whmcs_id",
    ]

    @classmethod
    def find_by_whmcs_server_id(cls, server_id):
        return cls.find(server_id)
