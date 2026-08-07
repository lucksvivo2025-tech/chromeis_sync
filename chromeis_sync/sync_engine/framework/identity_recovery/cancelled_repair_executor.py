from chromeis_sync.sync_engine.framework.identity_recovery.invoice_cloner import (
    InvoiceCloner,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_deleter import (
    InvoiceDeleter,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_inserter import (
    InvoiceInserter,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_mutator import (
    InvoiceMutator,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_reconstructor import (
    InvoiceReconstructor,
)

from chromeis_sync.sync_engine.framework.identity_recovery.whmcs_snapshot_provider import (
    WHMCSSnapshotProvider,
)


class CancelledRepairExecutor:

    @staticmethod
    def execute(
        plan,
        commit=False,
    ):

        clone = InvoiceCloner.clone(
            plan["erp_invoice"]
        )

        snapshot = WHMCSSnapshotProvider.load(
            plan["invoice"]
        )

        reconstruction = InvoiceReconstructor.reconstruct(
            snapshot
        )

        InvoiceMutator.delete_all_rows(
            clone
        )

        for row in reconstruction["rows"]:

            InvoiceMutator.add_row(
                clone,
                row,
            )

        InvoiceMutator.recalculate(
            clone
        )

        if not commit:

            return {
                "success": True,
                "strategy": "CANCELLED_RECREATE",
                "commit": False,
                "source_invoice": plan["erp_invoice"],
                "old_rows": len(snapshot.items),
                "new_rows": len(clone.items),
                "total": clone.grand_total,
                "message": (
                    "Cancelled invoice rebuilt successfully."
                ),
            }

        #
        # Delete the old ERP mirror first.
        # This releases the UNIQUE WHMCS identity.
        #

        InvoiceDeleter.delete(
            InvoiceMutator.load(
                plan["erp_invoice"]
            )
        )

        clone = InvoiceInserter.insert(
            clone
        )

        return {
            "success": True,
            "strategy": "CANCELLED_RECREATE",
            "commit": True,
            "source_invoice": plan["erp_invoice"],
            "new_invoice": clone.name,
            "rows": len(clone.items),
            "message": (
                "Cancelled invoice recreated successfully."
            ),
        }
