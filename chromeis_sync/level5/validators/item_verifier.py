from decimal import Decimal


class ItemVerifier:

    TOLERANCE = Decimal("0.0001")

    @classmethod
    def verify(cls, api_items, erp_items):

        differences = []

        whmcs_items = (
            api_items.get("item", [])
            if isinstance(api_items, dict)
            else []
        )

        erp_items = erp_items or []

        if len(whmcs_items) != len(erp_items):
            differences.append({
                "field": "items",
                "reason": "Item count mismatch",
                "whmcs_count": len(whmcs_items),
                "erp_count": len(erp_items),
            })

        for index, wh_item in enumerate(whmcs_items):

            if index >= len(erp_items):
                break

            erp_item = erp_items[index]

            wh_amount = Decimal(
                str(wh_item.get("amount") or 0)
            )

            erp_amount = Decimal(
                str(erp_item.get("amount") or 0)
            )

            if abs(wh_amount - erp_amount) > cls.TOLERANCE:

                differences.append({
                    "field": "items",
                    "index": index,
                    "whmcs_description": wh_item.get(
                        "description"
                    ),
                    "whmcs_amount": float(wh_amount),
                    "erp_description": erp_item.get(
                        "description"
                    ),
                    "erp_amount": float(erp_amount),
                })

        return differences
