from decimal import Decimal


class InvoiceResultClassifier:

    @staticmethod
    def classify(result, evidence):

        api = evidence.get("api") or {}
        mirror = evidence.get("mirror") or {}
        erp = evidence.get("erp") or {}

        differences = result.get("differences") or []

        # ---------------------------------------------------------
        # No differences
        # ---------------------------------------------------------

        if not differences:
            return "PROPER"

        fields = {
            d.get("field")
            for d in differences
        }

        # ---------------------------------------------------------
        # Credit allocation / relationship exception
        # ---------------------------------------------------------

        if (
            "credit_invoice_allocation" in fields
            or "credit_relationship" in fields
        ):
            return "CREDIT_ALLOCATION"

        # ---------------------------------------------------------
        # Tax presentation
        # ---------------------------------------------------------

        wh_tax = Decimal(
            str(api.get("tax") or 0)
        )

        erp_tax = Decimal(
            str(
                sum(
                    Decimal(str(t.get("tax_amount") or 0))
                    for t in erp.get("taxes", [])
                )
            )
        )

        wh_subtotal = Decimal(
            str(api.get("subtotal") or 0)
        )

        erp_net = Decimal(
            str(erp.get("net_total") or 0)
        )

        if (
            wh_tax > 0
            and wh_subtotal == erp_net
            and erp_tax == 0
            and fields.issubset({
                "tax",
                "tax_structure",
            })
        ):
            return "TAX_PRESENTATION_ONLY"

        # ---------------------------------------------------------
        # WHMCS credit presentation
        #
        # A credit can change the WHMCS displayed total while ERP
        # retains the gross invoice value.
        #
        # This is presentation-only ONLY when the ERP gross/net
        # structure agrees with the WHMCS invoice structure.
        # ---------------------------------------------------------

        wh_credit = Decimal(
            str(api.get("credit") or 0)
        )

        whmcs_credit_rows = (
            evidence.get("whmcs_credits") or []
        )

        credit_exists = (
            wh_credit > 0
            or any(
                Decimal(
                    str(abs(row.get("amount") or 0))
                ) > 0
                for row in whmcs_credit_rows
            )
        )

        gross_total_difference_only = fields.issubset(
            {
                "gross_total",
                "balance",
            }
        )

        if (
            credit_exists
            and wh_subtotal == erp_net
            and gross_total_difference_only
        ):
            return "WHMCS_CREDIT_PRESENTATION_ONLY"


        # ---------------------------------------------------------
        # Overpayment / customer-credit presentation
        #
        # Example:
        #
        # WHMCS invoice total = 28.00
        # WHMCS transaction = 28.09
        # WHMCS credit = 0.09
        # ERP invoice = 28.00
        # ERP payment = 28.09
        #
        # The invoice itself is correct. The extra payment is
        # represented as customer credit.
        # ---------------------------------------------------------

        whmcs_transactions = (
            evidence.get("whmcs_transactions") or []
        )

        erp_payments = (
            evidence.get("erp_payments") or []
        )

        whmcs_payment_amount = sum(
            (
                Decimal(
                    str(row.get("amountin") or 0)
                )
                for row in whmcs_transactions
            ),
            Decimal("0"),
        )

        erp_payment_amount = sum(
            (
                Decimal(
                    str(row.get("paid_amount") or 0)
                )
                for row in erp_payments
            ),
            Decimal("0"),
        )

        whmcs_invoice_total = Decimal(
            str(api.get("total") or 0)
        )

        whmcs_credit_rows = (
            evidence.get("whmcs_credits") or []
        )

        overpayment_credit = sum(
            (
                Decimal(
                    str(row.get("amount") or 0)
                )
                for row in whmcs_credit_rows
                if (
                    "overpayment"
                    in str(
                        row.get("description") or ""
                    ).lower()
                    and Decimal(
                        str(row.get("amount") or 0)
                    ) > 0
                )
            ),
            Decimal("0"),
        )

        if (
            "balance" in fields
            and whmcs_invoice_total == erp_net
            and whmcs_payment_amount == erp_payment_amount
            and whmcs_payment_amount > whmcs_invoice_total
            and overpayment_credit > 0
            and (
                whmcs_payment_amount
                - whmcs_invoice_total
            ).copy_abs()
            == overpayment_credit.copy_abs()
        ):
            return "WHMCS_CREDIT_PRESENTATION_ONLY"

        # ---------------------------------------------------------
        # Item difference
        #
        # An actual item difference is commercial unless another
        # explicit classification above applies.
        # ---------------------------------------------------------

        if "items" in fields:
            return "COMMERCIAL_DIFFERENCE"

        # ---------------------------------------------------------
        # Any remaining difference is a genuine commercial /
        # reconciliation difference.
        #
        # Never return an invalid classification value.
        # ---------------------------------------------------------

        return "COMMERCIAL_DIFFERENCE"
