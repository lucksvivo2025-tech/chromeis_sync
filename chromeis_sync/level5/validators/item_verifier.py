from decimal import Decimal
import html
import re


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

        matched_erp_indexes = set()


        # ---------------------------------------------------------
        # Item count evidence
        # ---------------------------------------------------------

        if len(whmcs_items) != len(erp_items):

            differences.append({
                "field": "items",
                "reason": "Item count mismatch",
                "whmcs_count": len(whmcs_items),
                "erp_count": len(erp_items),
            })


        # ---------------------------------------------------------
        # Match items by description + amount
        # instead of list position
        # ---------------------------------------------------------

        for wh_index, wh_item in enumerate(whmcs_items):

            wh_amount = Decimal(
                str(
                    wh_item.get("amount") or 0
                )
            )

            wh_description = cls._normalize_description(
                wh_item.get("description")
            )

            matched = False


            for erp_index, erp_item in enumerate(erp_items):

                if erp_index in matched_erp_indexes:
                    continue


                erp_amount = Decimal(
                    str(
                        erp_item.get("amount") or 0
                    )
                )


                erp_description = cls._normalize_description(
                    erp_item.get("description")
                )


                # Exact amount + normalized description match

                if (
                    abs(
                        wh_amount - erp_amount
                    )
                    <= cls.TOLERANCE
                    and
                    wh_description == erp_description
                ):

                    matched_erp_indexes.add(
                        erp_index
                    )

                    matched = True
                    break


            if matched:
                continue


            # -----------------------------------------------------
            # Fallback:
            # amount match only
            #
            # Handles harmless wording changes
            # -----------------------------------------------------

            for erp_index, erp_item in enumerate(erp_items):

                if erp_index in matched_erp_indexes:
                    continue


                erp_amount = Decimal(
                    str(
                        erp_item.get("amount") or 0
                    )
                )


                if (
                    abs(
                        wh_amount - erp_amount
                    )
                    <= cls.TOLERANCE
                ):

                    matched_erp_indexes.add(
                        erp_index
                    )

                    matched = True
                    break


            if not matched:

                differences.append({

                    "field": "items",

                    "index": wh_index,

                    "whmcs_description": (
                        wh_item.get("description")
                    ),

                    "whmcs_amount": float(
                        wh_amount
                    ),

                    "erp_description": None,

                    "erp_amount": None,

                    "reason": (
                        "No matching ERP item found"
                    ),
                })


        return differences



    @staticmethod
    def _normalize_description(value):

        if not value:
            return ""

        value = html.unescape(
            str(value)
        )

        value = value.lower()

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        return value.strip()
