from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.promotion import (
    PromotionRepository,
)


ENTITY = BaseEntity(

    #
    # Basic Information
    #

    name="Promotion",

    whmcs_table="tblpromotions",

    erp_doctype="Promotional Scheme",

    identity_field="custom_whmcs_promo_id",

    repository=PromotionRepository,

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

    description="WHMCS Promotion",

)
