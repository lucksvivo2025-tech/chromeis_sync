from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class DomainRepository(BaseRepository):

    doctype = "Sales Invoice Item"

    whmcs_field = "custom_whmcs_domain_id"

    default_fields = [
        "parent",
        "item_code",
        "item_name",
        "custom_whmcs_domain_id",
    ]

    @classmethod
    def find_by_whmcs_domain_id(cls, domain_id):
        return cls.find(domain_id)
