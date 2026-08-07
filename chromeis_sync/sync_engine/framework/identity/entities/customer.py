from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.customer import (
    CustomerRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Customer",

    whmcs_table="tblclients",

    erp_doctype="Customer",

    identity_field="custom_whmcs_client_id",

    repository=CustomerRepository,

    #
    # Matching fields
    #

    match_fields=[
        "email",
    ],

    #
    # Parent dependencies
    #

    depends_on=[],

    #
    # WHMCS relationship mapping
    #

    relationship_fields={},

    #
    # Description
    #

    description="WHMCS Customer",

)
