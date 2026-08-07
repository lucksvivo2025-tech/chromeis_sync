from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.server import (
    ServerRepository,
)


ENTITY = BaseEntity(

    name="Server",

    whmcs_table="tblservers",

    erp_doctype="Server",

    identity_field="custom_whmcs_server_id",

    repository=ServerRepository,

    match_fields=[
        "hostname",
        "ipaddress",
    ],

    description="WHMCS Servers",

)
