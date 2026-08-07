from chromeis_sync.sync_engine.framework.identity_recovery.repair_executor import (
    RepairExecutor,
)


class RepairPlanner:

    @staticmethod
    def build(invoice_id):

        result = RepairExecutor.execute(
            invoice_id,
            commit=False,
        )

        actions = []

        transformation = result["transformation_status"]

        if transformation == "IDENTICAL":

            actions.append(
                {
                    "step": 1,
                    "action": "VERIFY",
                    "target": "Invoice",
                    "description": "Invoice already matches WHMCS",
                }
            )

        elif transformation == "MERGED":

            actions.extend(
                [
                    {
                        "step": 1,
                        "action": "RECOVER_IDENTITY",
                        "target": "Invoice Items",
                        "description": "Recover merged identities",
                    },
                    {
                        "step": 2,
                        "action": "SPLIT_ROWS",
                        "target": "Sales Invoice Item",
                        "description": "Split merged ERP rows",
                    },
                ]
            )

        elif transformation == "SPLIT":

            actions.extend(
                [
                    {
                        "step": 1,
                        "action": "RECOVER_IDENTITY",
                        "target": "Invoice Items",
                        "description": "Recover split identities",
                    },
                    {
                        "step": 2,
                        "action": "MERGE_ROWS",
                        "target": "Sales Invoice Item",
                        "description": "Merge ERP rows where required",
                    },
                ]
            )

        elif transformation == "COLLAPSED":

            actions.append(
                {
                    "step": 1,
                    "action": "RESTORE_UNSUPPORTED",
                    "target": "Invoice Items",
                    "description": "Restore collapsed legacy items",
                }
            )

        elif transformation == "PARTIAL":

            actions.append(
                {
                    "step": 1,
                    "action": "MANUAL_MATCH",
                    "target": "Invoice Items",
                    "description": "Recover unmatched identities",
                }
            )

        elif transformation == "LEGACY_FREEFORM":

            actions.append(
                {
                    "step": 1,
                    "action": "MANUAL_REVIEW",
                    "target": "Invoice",
                    "description": "Legacy freeform invoice requires review",
                }
            )

        elif transformation == "EMPTY":

            actions.append(
                {
                    "step": 1,
                    "action": "INVESTIGATE",
                    "target": "Invoice",
                    "description": "No WHMCS items found",
                }
            )

        next_step = len(actions) + 1

        actions.append(
            {
                "step": next_step,
                "action": "VERIFY_TOTALS",
                "target": "Invoice",
                "description": "Verify invoice totals",
            }
        )

        actions.append(
            {
                "step": next_step + 1,
                "action": "VERIFY_LEDGER",
                "target": "General Ledger",
                "description": "Verify accounting impact",
            }
        )

        return {
            "invoice": invoice_id,
            "erp_invoice": result["erp_invoice"],
            "identity_status": result["identity_status"],
            "transformation": transformation,
            "actions": actions,
            "ready": result["success"],
        }
