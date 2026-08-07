from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)
from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)
from chromeis_sync.sync_engine.framework.identity_recovery.repair_strategies import (
    RepairStrategies,
)


class RepairExecutor:

    @staticmethod
    def execute(invoice_id, commit=False):

        recovery = IdentityRecoveryEngine.invoice(
            invoice_id,
            commit=commit,
        )

        analysis = recovery["analysis"]

        transformation = (
            TransformationDetector.analyze(
                invoice_id
            )
        )

        strategy = RepairStrategies.dispatch(
            invoice_id,
            analysis,
            commit=commit,
        )

        return {

            "invoice": invoice_id,

            "erp_invoice": analysis.erp_invoice,

            "identity_status": analysis.status,

            "transformation_status": transformation["status"],

            "strategy": strategy.get(
                "strategy"
            ),

            "reason": strategy.get(
                "reason"
            ),

            "success": strategy.get(
                "success",
                False,
            ),

            "updated": strategy.get(
                "updated",
                0,
            ),

            "commit": commit,
        }
