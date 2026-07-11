import frappe

from chromeis_sync.migration_audit.models import VerificationResult


class InvoiceVerifier:

    def verify(self, snapshot, new_invoice, target_currency):

        result = VerificationResult()

        old = snapshot["header"]

        # ----------------------------------------------------
        # Identity Validation
        # ----------------------------------------------------

        identity_fields = [
            "customer",
            "company",
            "custom_whmcs_client_id",
            "whmcs_invoice_id",
        ]

        for field in identity_fields:

            if old.get(field) != getattr(new_invoice, field, None):
                result.passed = False
                result.errors.append(
                    f"{field} mismatch"
                )

        # ----------------------------------------------------
        # Currency Validation
        # ----------------------------------------------------

        if new_invoice.currency != target_currency:
            result.passed = False
            result.errors.append(
                f"Currency mismatch ({new_invoice.currency} != {target_currency})"
            )

        # ----------------------------------------------------
        # Grand Total Validation
        # ----------------------------------------------------

        if round(float(old.get("grand_total", 0)), 2) != round(float(new_invoice.grand_total), 2):
            result.passed = False
            result.errors.append(
                "Grand total mismatch"
            )

        # ----------------------------------------------------
        # Item Count Validation
        # ----------------------------------------------------

        if len(snapshot["items"]) != len(new_invoice.items):
            result.passed = False
            result.errors.append(
                "Item count mismatch"
            )

            return result

        # ----------------------------------------------------
        # Item Validation
        # ----------------------------------------------------

        for index, old_item in enumerate(snapshot["items"]):

            new_item = new_invoice.items[index]

            comparisons = [

                (
                    "item_code",
                    old_item.get("item_code"),
                    new_item.item_code
                ),

                (
                    "qty",
                    round(float(old_item.get("qty", 0)), 6),
                    round(float(new_item.qty), 6)
                ),

                (
                    "rate",
                    round(float(old_item.get("rate", 0)), 6),
                    round(float(new_item.rate), 6)
                ),

                (
                    "income_account",
                    old_item.get("income_account"),
                    new_item.income_account
                ),

                (
                    "cost_center",
                    old_item.get("cost_center"),
                    new_item.cost_center
                ),

            ]

            for field, old_value, new_value in comparisons:

                if old_value != new_value:

                    result.passed = False

                    result.errors.append(
                        f"Item {index + 1}: {field} mismatch "
                        f"({old_value} != {new_value})"
                    )

        return result
