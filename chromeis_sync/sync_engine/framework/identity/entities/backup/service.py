from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.service import (
    ServiceRepository,
)


ENTITY = BaseEntity(

    name="Service",

    whmcs_table="tblhosting",

    erp_doctype="Subscription",

    identity_field="whmcs_service_id",

    repository=ServiceRepository,

    match_fields=[
        "domain",
        "packageid",
    ],

    description="WHMCS Hosting Services",

)
