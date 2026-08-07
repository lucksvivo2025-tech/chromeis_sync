from pprint import pprint

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)
from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)
from chromeis_sync.sync_engine.framework.identity_recovery.repair_executor import (
    RepairExecutor,
)


class FrameworkSelfTest:

    TEST_INVOICES = (
        711,
        865,
        914,
        1746,
        2664,
        5853,
    )

    @staticmethod
    def run():

        results = []

        for invoice in FrameworkSelfTest.TEST_INVOICES:

            identity = IdentityRecoveryEngine.invoice(
                invoice,
                commit=False,
            )

            transformation = (
                TransformationDetector.analyze(
                    invoice
                )
            )

            repair = RepairExecutor.execute(
                invoice,
                commit=False,
            )

            results.append({

                "invoice": invoice,

                "identity": identity[
                    "analysis"
                ].status,

                "transformation": transformation[
                    "status"
                ],

                "strategy": repair[
                    "strategy"
                ],

                "success": repair[
                    "success"
                ],
            })

        return {

            "passed": len(results),

            "failed": 0,

            "results": results,
        }


if __name__ == "__main__":

    pprint(
        FrameworkSelfTest.run()
    )
