from chromeis_sync.sync_engine.framework.builders.base import (
    BaseBuilder,
)


class ServerBuilder(BaseBuilder):
    """
    Builds an ERPNext Server payload
    from a WHMCS tblservers row.
    """

    def build(self):

        row = self.source

        return {
            "doctype": "Server",
            "data": {
                "server_name": row["name"],
                "ip_address": row["ipaddress"],
                "provider": "Other",
                "whmcs_id": row["id"],
            },
        }
