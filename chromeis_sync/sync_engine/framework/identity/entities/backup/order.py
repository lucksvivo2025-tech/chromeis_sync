from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.order import (
    OrderRepository,
)


ENTITY = BaseEntity(

    name="Order",

    whmcs_table="tblorders",

    erp_doctype="Sales Order",

    identity_field="custom_whmcs_order_id",

    repository=OrderRepository,

    match_fields=[
        "userid",
        "invoiceid",
    ],

    description="WHMCS Orders",

)
