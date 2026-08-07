from chromeis_sync.sync_engine.framework.synchronizers.base import (
    BaseSynchronizer,
)


class ServiceSynchronizer(BaseSynchronizer):
    """
    Service Synchronizer.
    """

    entity = "service"

    @classmethod
    def synchronize(cls, identifier):

        return {
            "entity": cls.entity,
            "identifier": str(identifier),
            "status": "READY",
        }
