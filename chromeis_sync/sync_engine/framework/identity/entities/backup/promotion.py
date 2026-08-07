from chromeis_sync.sync_engine.framework.identity.base_entity import (
    BaseEntity,
)

from chromeis_sync.sync_engine.framework.repositories.promotion import (
    PromotionRepository,
)


ENTITY = BaseEntity(

    name="Promotion",

    whmcs_table="tblpromotions",

    erp_doctype="Promotional Scheme",

    identity_field="custom_whmcs_promo_id",

    repository=PromotionRepository,

    match_fields=[
        "code",
    ],

    description="WHMCS Promotions",

)
