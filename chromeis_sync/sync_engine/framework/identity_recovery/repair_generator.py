class RepairGenerator:

    @staticmethod
    def generate(comparison):

        if not comparison.get("success", True):
            return {
                "success": False,
                "reason": comparison.get("reason"),
            }

        operations = []

        for difference in comparison["differences"]:

            dtype = difference["type"]

            #
            # Existing ERP row must be updated.
            #

            if dtype == "ROW_CHANGED":

                operations.append(
                    {
                        "operation": "UPDATE_ROW",
                        "target": "Sales Invoice Item",
                        "erp_row": difference["erp_row"],
                        "changes": difference["changes"],
                        "current": difference["current"],
                        "expected": difference["expected"],
                    }
                )

            #
            # ERP is missing this row.
            #

            elif dtype == "MISSING_IN_ERP":

                operations.append(
                    {
                        "operation": "ADD_ROW",
                        "target": "Sales Invoice Item",
                        "data": difference["expected"],
                    }
                )

            #
            # ERP has a row that should not exist.
            #

            elif dtype == "EXTRA_IN_ERP":

                operations.append(
                    {
                        "operation": "DELETE_ROW",
                        "target": "Sales Invoice Item",
                        "erp_row": difference["erp_row"],
                        "current": difference["current"],
                    }
                )

        return {

            "success": True,

            "invoice": comparison["invoice"],

            "erp_invoice": comparison["erp_invoice"],

            "repair_required": len(operations) > 0,

            "operation_count": len(operations),

            "operations": operations,

        }
