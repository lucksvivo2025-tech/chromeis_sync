import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.repair_plan_builder import (
    RepairPlanBuilder,
)


class RepairExecutorV2:

    @staticmethod
    def execute(invoice_id, commit=False):

        plan = RepairPlanBuilder.build(invoice_id)

        if not plan["success"]:
            return plan

        invoice = frappe.get_doc(
            "Sales Invoice",
            plan["erp_invoice"],
        )

        executed = []

        for operation in plan["operations"]:

            if operation["operation"] == "UPDATE_ROW":

                #
                # For now we only record what would change.
                # Real updates will be implemented next.
                #

                executed.append(
                    {
                        "operation": "UPDATE_ROW",
                        "status": "DRY_RUN",
                        "row": operation["row"],
                        "changes": operation["changes"],
                    }
                )

            elif operation["operation"] == "ADD_ROW":

                executed.append(
                    {
                        "operation": "ADD_ROW",
                        "status": "DRY_RUN",
                        "data": operation["data"],
                    }
                )

            elif operation["operation"] == "DELETE_ROW":

                executed.append(
                    {
                        "operation": "DELETE_ROW",
                        "status": "DRY_RUN",
                        "data": operation["data"],
                    }
                )

        #
        # Future implementation:
        #
        # if commit:
        #     invoice.save()
        #     frappe.db.commit()
        #

        return {

            "success": True,

            "invoice": invoice_id,

            "erp_invoice": invoice.name,

            "commit": commit,

            "dry_run": not commit,

            "repair_required": plan["repair_required"],

            "operation_count": len(executed),

            "executed": executed,

        }
