from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class PromotionRepository(BaseRepository):

    doctype = "Pricing Rule"

    whmcs_field = "custom_whmcs_promo_code"

    default_fields = [
        "name",
        "title",
        "custom_whmcs_promo_code",
        "disable",
    ]

    @classmethod
    def find_by_whmcs_promo_code(cls, promo_code):
        return cls.find(promo_code)
