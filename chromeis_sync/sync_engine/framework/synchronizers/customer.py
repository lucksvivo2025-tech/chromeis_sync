from chromeis_sync.sync_engine.framework.identity.registry import (
    get_entity,
)

from chromeis_sync.sync_engine.framework.synchronizers.base import (
    BaseSynchronizer,
)


class CustomerSynchronizer(BaseSynchronizer):
    """
    Synchronizes a WHMCS Customer.

    Version 1:
        • Identity lookup only.
        • No create/update yet.
    """

    entity = "customer"

    @classmethod
    def synchronize(cls, identifier):

        entity = get_entity(cls.entity)

        result = entity.repository.find(identifier)

        return {

            "entity": cls.entity,

            "identifier": str(identifier),

            "found": result.found,

            "status": str(result.status),

            "document": result.document_name,

            "reason": result.reason,

        }
