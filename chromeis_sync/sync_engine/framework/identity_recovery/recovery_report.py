from collections import Counter

from chromeis_sync.sync_engine.framework.identity_recovery.execute import (
    IdentityRecoveryExecutor,
)


class RecoveryReport:

    @staticmethod
    def run(limit=None, commit=False):

        result = IdentityRecoveryExecutor.run(
            limit=limit,
            commit=commit,
        )

        status_counter = Counter()

        rows_updated = 0

        for row in result["details"]:

            status_counter[row["status"]] += 1
            rows_updated += row["updated"]

        return {

            "mode": (
                "COMMIT"
                if commit
                else "DRY_RUN"
            ),

            "total": result["total"],

            "processed": result["processed"],

            "recoverable": result["recoverable"],

            "skipped": result["skipped"],

            "failed": result["failed"],

            "updated_rows": rows_updated,

            "statuses": dict(
                sorted(
                    status_counter.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),

            "details": result["details"],
        }
