import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.recover import (
    IdentityRecovery,
)


class BatchIdentityRecovery:

    @staticmethod
    def execute(commit=False):

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["is", "set"],
            },
            fields=[
                "whmcs_invoice_id",
            ],
            order_by="cast(whmcs_invoice_id as unsigned)",
        )

        summary = {
            "processed": 0,
            "recovered": 0,
            "failed": 0,
            "skipped": 0,
        }

        for row in invoices:

            invoice_id = int(row.whmcs_invoice_id)

            try:

                result = IdentityRecovery.invoice(
                    invoice_id,
                    commit=False,
                )

                summary["processed"] += 1

                if result.get("success"):

                    summary["recovered"] += result.get(
                        "updated_count",
                        0,
                    )

                else:

                    summary["skipped"] += 1

                    status = result.get("status", "UNKNOWN")

                    summary.setdefault("status_breakdown", {})

                    summary["status_breakdown"][status] = (
                    summary["status_breakdown"].get(status, 0) + 1
                )

            except Exception as e:

                status = "EXCEPTION"

                summary.setdefault("status_breakdown", {})

                summary["status_breakdown"][status] = (
                summary["status_breakdown"].get(status, 0) + 1
                )


                summary["failed"] += 1

                print(
                    invoice_id,
                    str(e),
                )

        if commit:

            frappe.db.commit()

        else:

            frappe.db.rollback()

        return summary
