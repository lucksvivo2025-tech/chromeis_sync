from chromeis_sync.sync_engine.framework.repositories.base import BaseRepository


class ServiceRepository(BaseRepository):

    doctype = "Subscription"

    whmcs_field = "whmcs_service_id"

    default_fields = [
        "name",
        "party",
        "status",
        "start_date",
        "end_date",
        "whmcs_service_id",
    ]

    @classmethod
    def find_by_whmcs_service_id(cls, service_id):
        return cls.find(service_id)
