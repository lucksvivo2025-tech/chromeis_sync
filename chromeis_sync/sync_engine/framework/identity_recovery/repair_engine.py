import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)
from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)
from chromeis_sync.sync_engine.framework.identity_recovery.repair_strategies import (
    RepairStrategies,
)


class IdentityRepairEngine:

    @staticmethod
    def repair(invoice_id, commit=False):

        recovery = IdentityRecoveryEngine.invoice(
            invoice_id,
            commit=commit,
        )

        analysis = recovery["analysis"]

        transformation = TransformationDetector.analyze(
            invoice_id
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

            "transformation": transformation["status"],

            "repaired": strategy["success"],

            "updated_rows": strategy["updated"],

            "reason": strategy["reason"],

            "commit": commit,
        }

    @staticmethod
    def run(limit=None, commit=False):

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["!=", ""],
            },
            fields=[
                "whmcs_invoice_id",
            ],
            order_by="creation asc",
            limit_page_length=limit or 100000,
        )

        repaired = 0
        failed = 0
        updated_rows = 0

        details = []

        for row in invoices:

            result = IdentityRepairEngine.repair(
                int(row.whmcs_invoice_id),
                commit=commit,
            )

            details.append(result)

            if result["repaired"]:
                repaired += 1
                updated_rows += result["updated_rows"]
            else:
                failed += 1

        return {

            "mode": (
                "COMMIT"
                if commit
                else "DRY_RUN"
            ),

            "total": len(invoices),

            "repaired": repaired,

            "failed": failed,

            "updated_rows": updated_rows,

            "details": details,
        }
