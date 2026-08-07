from chromeis_sync.sync_engine.framework.identity.registry import (
    get_entity,
)

from chromeis_sync.sync_engine.framework.planner.execution_plan import (
    ExecutionPlan,
    ExecutionStep,
)

from chromeis_sync.sync_engine.framework.relationships.relationship_loader import (
    RelationshipLoader,
)


class DependencyPlanner:
    """
    Builds a dependency-aware execution plan using
    entity metadata and WHMCS relationships.
    """

    @classmethod
    def build(cls, entity_name, identifier):

        plan = ExecutionPlan(
            root_entity=entity_name,
            root_identifier=str(identifier),
        )

        cls._expand(
            entity_name,
            identifier,
            plan,
            visited=set(),
        )

        return plan

    @classmethod
    def _expand(
        cls,
        entity_name,
        identifier,
        plan,
        visited,
    ):

        key = (entity_name, str(identifier))

        if key in visited:
            return

        visited.add(key)

        entity = get_entity(entity_name)

        relationships = RelationshipLoader.load(
            entity_name,
            identifier,
        ) or {}

        #
        # Expand parent entities first
        #

        for parent in entity.depends_on:

            parent_id = relationships.get(parent)

            if parent_id is not None:

                cls._expand(
                    parent,
                    parent_id,
                    plan,
                    visited,
                )

        #
        # Then add the current entity
        #

        plan.add_step(
            ExecutionStep(
                entity=entity_name,
                identifier=str(identifier),
                depends_on=list(entity.depends_on),
            )
        )
