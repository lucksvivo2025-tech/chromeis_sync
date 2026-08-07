from chromeis_sync.sync_engine.framework.identity.registry import (
    get_entity,
)

from chromeis_sync.sync_engine.framework.whmcs.client import (
    WHMCSClient,
)


class RelationshipLoader:
    """
    Generic relationship loader.

    Given an entity and its WHMCS identifier, returns the
    WHMCS identifiers of all parent entities defined in the
    entity metadata.
    """

    @classmethod
    def load(cls, entity_name, identifier):

        entity = get_entity(entity_name)

        row = WHMCSClient.get_row(
            entity.whmcs_table,
            identifier,
        )

        if not row:
            return None

        relationships = {}

        for parent, field in entity.relationship_fields.items():

            relationships[parent] = row.get(field)

        return relationships
