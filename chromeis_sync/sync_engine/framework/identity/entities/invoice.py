from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.invoice import (
    InvoiceRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Invoice",

    whmcs_table="tblinvoices",

    erp_doctype="Sales Invoice",

    identity_field="whmcs_invoice_id",

    repository=InvoiceRepository,

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

    description="WHMCS Invoice",

)
