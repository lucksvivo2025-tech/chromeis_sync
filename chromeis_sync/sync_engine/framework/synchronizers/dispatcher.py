from chromeis_sync.sync_engine.framework.synchronizers.customer import (
    CustomerSynchronizer,
)

from chromeis_sync.sync_engine.framework.synchronizers.invoice import (
    InvoiceSynchronizer,
)

from chromeis_sync.sync_engine.framework.synchronizers.service import (
    ServiceSynchronizer,
)


class SynchronizerDispatcher:
    """
    Routes execution to the appropriate entity synchronizer.
    """

    REGISTRY = {
        "customer": CustomerSynchronizer,
        "invoice": InvoiceSynchronizer,
        "service": ServiceSynchronizer,
    }

    @classmethod
    def dispatch(cls, entity_name, identifier):

        synchronizer = cls.REGISTRY.get(entity_name)

        if synchronizer is None:
            return {
                "entity": entity_name,
                "identifier": str(identifier),
                "status": "NO_SYNCHRONIZER",
            }

        return synchronizer.synchronize(identifier)
