from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.service import (
    ServiceRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Service",

    whmcs_table="tblhosting",

    erp_doctype="Subscription",

    identity_field="whmcs_service_id",

    repository=ServiceRepository,

    #
    # Matching fields
    #

    match_fields=[
        "domain",
        "packageid",
    ],

    #
    # Parent dependencies
    #

    depends_on=[
        "customer",
        "product",
        "server",
        "order",
    ],

    #
    # WHMCS relationship mapping
    #

    relationship_fields={

        "customer": "userid",

        "product": "packageid",

        "server": "server",

        "order": "orderid",

    },

    #
    # Description
    #

    description="WHMCS Hosting Service",

)
