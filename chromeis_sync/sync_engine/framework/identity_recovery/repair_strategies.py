from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)

from chromeis_sync.sync_engine.framework.identity_recovery.repair_actions import (
    IdenticalRepair,
    SplitRepair,
    MergedRepair,
    CollapsedRepair,
    PartialRepair,
    LegacyFreeformRepair,
    EmptyRepair,
)


class RepairStrategies:

    @staticmethod
    def dispatch(invoice_id, analysis, commit=False):

        transformation = TransformationDetector.analyze(
            invoice_id
        )

        status = transformation["status"]

        if status == "IDENTICAL":

            return IdenticalRepair.execute(
                invoice_id,
                analysis,
                commit,
            )

        elif status == "SPLIT":

            return SplitRepair.execute(
                invoice_id,
                analysis,
                commit,
            )

        elif status == "MERGED":

            return MergedRepair.execute(
                invoice_id,
                analysis,
                commit,
            )

        elif status == "COLLAPSED":

            return CollapsedRepair.execute(
                invoice_id,
                analysis,
                commit,
            )

        elif status == "LEGACY_FREEFORM":

            return LegacyFreeformRepair.execute(
                invoice_id,
                analysis,
                commit,
            )

        elif status == "EMPTY":

            return EmptyRepair.execute(
                invoice_id,
                analysis,
                commit,
            )

        else:

            return PartialRepair.execute(
                invoice_id,
                analysis,
                commit,
            )
