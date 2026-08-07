from chromeis_sync.sync_engine.framework.identity_recovery.invoice_comparator import (
    InvoiceComparator,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_identity_resolver import (
    InvoiceIdentityResolver,
)

from chromeis_sync.sync_engine.framework.identity_recovery.repair_generator import (
    RepairGenerator,
)


class RepairPlanBuilder:

    @staticmethod
    def build(invoice_id):

        invoice = InvoiceIdentityResolver.get(
            invoice_id
        )

        comparison = InvoiceComparator.compare(
            invoice_id
        )

        if not comparison["success"]:

            return {
                "success": False,
                "invoice": invoice_id,
                "reason": comparison["reason"],
            }

        repair = RepairGenerator.generate(
            comparison
        )

        plan = {

            "success": True,

            "invoice": invoice_id,

            "erp_invoice": invoice.name,

            "repair_required": repair["repair_required"],

            "operation_count": repair["operation_count"],

            "operations": repair["operations"],

            "summary": {
                "add_rows": 0,
                "update_rows": 0,
                "delete_rows": 0,
            },

        }

        for operation in repair["operations"]:

            if operation["operation"] == "ADD_ROW":

                plan["summary"]["add_rows"] += 1

            elif operation["operation"] == "UPDATE_ROW":

                plan["summary"]["update_rows"] += 1

            elif operation["operation"] == "DELETE_ROW":

                plan["summary"]["delete_rows"] += 1

        return plan
