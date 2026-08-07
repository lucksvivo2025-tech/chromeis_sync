from chromeis_sync.sync_engine.framework.identity_recovery.repair_verifier import (
    RepairVerifier,
)

from chromeis_sync.sync_engine.framework.identity_recovery.repair_plan_builder import (
    RepairPlanBuilder,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_mutator import (
    InvoiceMutator,
)

from chromeis_sync.sync_engine.framework.identity_recovery.repair_strategy_resolver import (
    RepairStrategyResolver,
)

from chromeis_sync.sync_engine.framework.identity_recovery.cancelled_repair_executor import (
    CancelledRepairExecutor,
)


class RepairCommitter:

    @staticmethod
    def execute(invoice_id, commit=False):

        verification = RepairVerifier.verify(
            invoice_id
        )

        if not verification["can_commit"]:

            return {
                "success": False,
                "invoice": invoice_id,
                "commit": commit,
                "verification": verification,
                "message": "Repair blocked by verifier.",
            }

        plan = RepairPlanBuilder.build(
            invoice_id
        )

        if not plan["success"]:

            return plan

        invoice = InvoiceMutator.load(
            plan["erp_invoice"]
        )

        strategy = RepairStrategyResolver.resolve(
            invoice
        )

        #
        # Dry Run
        #

        if not commit:

            return {
                "success": True,
                "invoice": invoice_id,
                "erp_invoice": plan["erp_invoice"],
                "strategy": strategy,
                "commit": False,
                "operation_count": len(
                    plan["operations"]
                ),
                "operations": plan["operations"],
                "message": "Dry run successful.",
            }

        #
        # Strategy Dispatcher
        #

        if strategy == "CANCELLED_RECREATE":

            return CancelledRepairExecutor.execute(
                plan,
                commit=True,
            )

        if strategy == "DRAFT_REBUILD":

            raise NotImplementedError(
                "DRAFT_REBUILD not implemented."
            )

        if strategy == "SUBMITTED_RECREATE":

            raise NotImplementedError(
                "SUBMITTED_RECREATE not implemented."
            )

        raise Exception(
            f"Unknown repair strategy: {strategy}"
        )
