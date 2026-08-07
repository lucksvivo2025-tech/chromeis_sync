from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.payment import (
    PaymentRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Payment",

    whmcs_table="tblaccounts",

    erp_doctype="Payment Entry",

    identity_field="custom_whmcs_transaction_id",

    repository=PaymentRepository,

    #
    # Matching fields
    #

    match_fields=[
        "transid",
    ],

    #
    # Parent dependencies
    #

    depends_on=[
        "customer",
        "invoice",
    ],

    #
    # WHMCS relationship mapping
    #

    relationship_fields={

        "customer": "userid",

        "invoice": "invoiceid",

    },

    #
    # Description
    #

    description="WHMCS Payment",

)
