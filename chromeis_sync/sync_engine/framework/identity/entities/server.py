from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.server import (
    ServerRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Server",

    whmcs_table="tblservers",

    erp_doctype="Server",

    identity_field="whmcs_id",

    repository=ServerRepository,

    #
    # Matching fields
    #

    match_fields=[],

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

    description="WHMCS Server",

)
