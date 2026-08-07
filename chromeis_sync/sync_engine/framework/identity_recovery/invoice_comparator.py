import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_identity_resolver import (
    InvoiceIdentityResolver,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_reconstructor import (
    InvoiceReconstructor,
)

from chromeis_sync.sync_engine.framework.identity_recovery.whmcs_snapshot_provider import (
    WHMCSSnapshotProvider,
)


class InvoiceComparator:

    @staticmethod
    def compare(invoice_id):

        snapshot = WHMCSSnapshotProvider.load(
            invoice_id
        )

        if not snapshot:

            return {
                "success": False,
                "reason": "WHMCS invoice not found",
            }

        reconstructed = InvoiceReconstructor.reconstruct(
            snapshot
        )

        erp_invoice = InvoiceIdentityResolver.get(
            invoice_id
        )

        if not erp_invoice:

            return {
                "success": False,
                "reason": "ERP invoice not found",
            }

        erp_rows = frappe.db.sql(
            """
            SELECT
                name,
                idx,
                item_code,
                item_name,
                description,
                qty,
                rate,
                amount,
                income_account
            FROM `tabSales Invoice Item`
            WHERE parent=%s
            ORDER BY idx
            """,
            (
                erp_invoice.name,
            ),
            as_dict=True,
        )

        remaining = reconstructed["rows"][:]

        differences = []

        #
        # Identity-based comparison
        #

        for erp in erp_rows:

            match = None

            for rebuilt in remaining:

                if (
                    rebuilt["item_code"] == erp["item_code"]
                    and float(rebuilt["amount"]) == float(erp["amount"])
                ):

                    match = rebuilt
                    break

            if not match:

                differences.append(
                    {
                        "type": "EXTRA_IN_ERP",
                        "erp_row": erp["name"],
                        "current": erp,
                    }
                )

                continue

            remaining.remove(
                match
            )

            row_diff = {}

            for field in (
                "item_code",
                "description",
                "qty",
                "rate",
                "amount",
                "income_account",
            ):

                left = erp.get(
                    field
                )

                right = match.get(
                    field
                )

                if left != right:

                    row_diff[field] = {
                        "erp": left,
                        "expected": right,
                    }

            if row_diff:

                differences.append(
                    {
                        "type": "ROW_CHANGED",
                        "erp_row": erp["name"],
                        "erp_idx": erp["idx"],
                        "current": erp,
                        "expected": match,
                        "changes": row_diff,
                    }
                )

        #
        # Missing ERP rows
        #

        for rebuilt in remaining:

            differences.append(
                {
                    "type": "MISSING_IN_ERP",
                    "expected": rebuilt,
                }
            )

        return {

            "success": True,

            "invoice": invoice_id,

            "erp_invoice": erp_invoice.name,

            "erp_rows": len(
                erp_rows
            ),

            "expected_rows": len(
                reconstructed["rows"]
            ),

            "differences": differences,

            "identical": len(
                differences
            )
            == 0,

        }
