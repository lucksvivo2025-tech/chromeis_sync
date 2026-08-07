from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.order import (
    OrderRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Order",

    whmcs_table="tblorders",

    erp_doctype="Sales Order",

    identity_field="custom_whmcs_order_id",

    repository=OrderRepository,

    #
    # Matching fields
    #

    match_fields=[],

    #
    # Parent dependencies
    #

    depends_on=[
        "customer",
    ],

    #
    # WHMCS relationship mapping
    #

    relationship_fields={

        "customer": "userid",

    },

    #
    # Description
    #

    description="WHMCS Order",

)
