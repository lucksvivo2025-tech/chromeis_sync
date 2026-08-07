from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.domain import (
    DomainRepository,
)


ENTITY = BaseEntity(

    name="Domain",

    whmcs_table="tbldomains",

    erp_doctype="Sales Invoice Item",

    identity_field="custom_whmcs_domain_id",

    repository=DomainRepository,

    match_fields=[
        "domain",
    ],

    description="WHMCS Domains",

)
