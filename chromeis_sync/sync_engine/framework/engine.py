from chromeis_sync.sync_engine.framework.planner.dependency_planner import (
    DependencyPlanner,
)

from chromeis_sync.sync_engine.framework.synchronizers.dispatcher import (
    SynchronizerDispatcher,
)


class SynchronizationEngine:
    """
    Generic synchronization engine.

    Builds a dependency plan and executes each step
    using the SynchronizerDispatcher.
    """

    @classmethod
    def synchronize(cls, entity_name, identifier):

        plan = DependencyPlanner.build(
            entity_name,
            identifier,
        )

        results = []

        for step in plan.steps:

            results.append(

                SynchronizerDispatcher.dispatch(
                    step.entity,
                    step.identifier,
                )

            )

        return results
