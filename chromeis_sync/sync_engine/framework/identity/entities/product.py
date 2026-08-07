from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.product import (
    ProductRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Product",

    whmcs_table="tblproducts",

    erp_doctype="Item",

    identity_field="custom_whmcs_product_id",

    repository=ProductRepository,

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

    description="WHMCS Product",

)
