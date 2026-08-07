from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.customer import (
    CustomerRepository,
)


ENTITY = BaseEntity(

    name="Customer",

    whmcs_table="tblclients",

    erp_doctype="Customer",

    identity_field="custom_whmcs_client_id",

    repository=CustomerRepository,

    match_fields=[
        "email",
    ],

    description="WHMCS Customers",

)
