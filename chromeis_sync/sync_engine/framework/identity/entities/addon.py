from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.addon import (
    AddonRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Addon",

    whmcs_table="tblhostingaddons",

    erp_doctype="Subscription",

    identity_field="custom_whmcs_addon_id",

    repository=AddonRepository,

    #
    # Matching fields
    #

    match_fields=[],

    #
    # Parent dependencies
    #

    depends_on=[
        "customer",
        "service",
        "product",
        "order",
    ],

    #
    # WHMCS relationship mapping
    #

    relationship_fields={

        "customer": "userid",

        "service": "hostingid",

        "product": "addonid",

        "order": "orderid",

    },

    #
    # Description
    #

    description="WHMCS Hosting Addon",

)
