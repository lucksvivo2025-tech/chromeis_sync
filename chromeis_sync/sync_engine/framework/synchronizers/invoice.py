from chromeis_sync.sync_engine.framework.synchronizers.base import (
    BaseSynchronizer,
)


class InvoiceSynchronizer(BaseSynchronizer):
    """
    Invoice Synchronizer.
    """

    entity = "invoice"

    @classmethod
    def synchronize(cls, identifier):

        return {
            "entity": cls.entity,
            "identifier": str(identifier),
            "status": "READY",
        }
