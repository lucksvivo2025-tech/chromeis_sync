from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.invoice import (
    InvoiceRepository,
)


ENTITY = BaseEntity(

    name="Invoice",

    whmcs_table="tblinvoices",

    erp_doctype="Sales Invoice",

    identity_field="whmcs_invoice_id",

    repository=InvoiceRepository,

    match_fields=[],

    description="WHMCS Invoices",

)
