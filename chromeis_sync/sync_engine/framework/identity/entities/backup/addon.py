from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.addon import (
    AddonRepository,
)


ENTITY = BaseEntity(

    name="Addon",

    whmcs_table="tblhostingaddons",

    erp_doctype="Subscription",

    identity_field="custom_whmcs_addon_id",

    repository=AddonRepository,

    match_fields=[
        "hostingid",
        "addonid",
    ],

    description="WHMCS Hosting Addons",

)
