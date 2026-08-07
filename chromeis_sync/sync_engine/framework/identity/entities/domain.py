from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.domain import (
    DomainRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Domain",

    whmcs_table="tbldomains",

    erp_doctype="Sales Invoice Item",

    identity_field="custom_whmcs_domain_id",

    repository=DomainRepository,

    #
    # Matching fields
    #

    match_fields=[
        "domain",
    ],

    #
    # Parent dependencies
    #

    depends_on=[
        "customer",
        "order",
    ],

    #
    # WHMCS relationship mapping
    #

    relationship_fields={

        "customer": "userid",

        "order": "orderid",

    },

    #
    # Description
    #

    description="WHMCS Domain",

)
