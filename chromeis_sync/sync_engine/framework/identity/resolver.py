from chromeis_sync.sync_engine.framework.identity.registry import (
    get_entity,
)


class IdentityResolver:

    @staticmethod
    def resolve(entity, identity):

        entity_definition = get_entity(entity)

        repository = entity_definition.repository

        return repository.find(identity)
