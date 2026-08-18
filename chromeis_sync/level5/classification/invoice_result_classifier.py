from decimal import Decimal


class InvoiceResultClassifier:

    @staticmethod
    def classify(result, evidence):

        api = evidence.get("api") or {}
        mirror = evidence.get("mirror") or {}
        erp = evidence.get("erp") or {}

        differences = result.get("differences") or []

        # No differences = fully verified invoice
        if not differences:
            return "PROPER"

        fields = {
            d.get("field")
            for d in differences
        }

        # 1. Credit allocation
        if "credit_invoice_allocation" in fields:
            return "CREDIT_ALLOCATION"


        wh_tax = Decimal(str(api.get("tax") or 0))
        erp_tax = Decimal(str(
            sum(
                t.get("tax_amount",0)
                for t in erp.get("taxes",[])
            )
        ))

        wh_subtotal = Decimal(str(api.get("subtotal") or 0))
        erp_net = Decimal(str(erp.get("net_total") or 0))


        # 2. Tax presentation
        if (
            wh_tax > 0
            and
            wh_subtotal == erp_net
            and
            erp_tax == 0
        ):
            return "TAX_PRESENTATION_ONLY"


        wh_credit = Decimal(str(api.get("credit") or 0))

        # 3. Credit presentation
        if (
            wh_credit > 0
            and
            wh_subtotal == erp_net
        ):
            return "WHMCS_CREDIT_PRESENTATION_ONLY"


        # 4. Item difference
        if "items" in fields:
            return "ITEM_DIFFERENCE"


        # 5. Commercial
        return "COMMERCIAL_DIFFERENCE"
