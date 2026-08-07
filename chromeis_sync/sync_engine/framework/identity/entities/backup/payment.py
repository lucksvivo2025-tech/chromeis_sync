from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.payment import (
    PaymentRepository,
)


ENTITY = BaseEntity(

    name="Payment",

    whmcs_table="tblaccounts",

    erp_doctype="Payment Entry",

    identity_field="custom_whmcs_transaction_id",

    repository=PaymentRepository,

    match_fields=[
        "invoiceid",
        "transid",
    ],

    description="WHMCS Payments",

)
