from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.product import (
    ProductRepository,
)


ENTITY = BaseEntity(

    name="Product",

    whmcs_table="tblproducts",

    erp_doctype="Item",

    identity_field="custom_whmcs_product_id",

    repository=ProductRepository,

    match_fields=[
        "gid",
        "name",
    ],

    description="WHMCS Products",

)
