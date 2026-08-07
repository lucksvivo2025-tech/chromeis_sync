import frappe

from chromeis_sync.sync_engine.framework.classification.legacy_invoice_classifier import (
    LegacyInvoiceClassifier,
)

from chromeis_sync.sync_engine.framework.models.invoice_analysis_result import (
    InvoiceAnalysisResult,
)


class InvoiceItemRecoveryAnalyzer:

    @staticmethod
    def analyze(invoice_id):

        result = InvoiceAnalysisResult(
            invoice=invoice_id,
        )

        whmcs_items = frappe.db.sql(
            """
            SELECT
                id,
                type,
                relid,
                description,
                amount
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
            """,
            (invoice_id,),
            as_dict=True,
        )

        result.total_whmcs_items = len(whmcs_items)

        erp_invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(invoice_id),
            },
            "name",
        )

        result.erp_invoice = erp_invoice

        if not erp_invoice:
            result.status = "ERP_MISSING"
            return result

        if not whmcs_items:
            result.status = "EMPTY"
            return result

        erp_rows = frappe.get_all(
            "Sales Invoice Item",
            filters={
                "parent": erp_invoice,
            },
            fields=[
                "name",
                "idx",
                "item_name",
                "amount",
                "custom_whmcs_service_id",
                "custom_whmcs_domain_id",
                "custom_whmcs_addon_id",
            ],
            order_by="idx",
        )

        used_rows = set()

        for item in whmcs_items:

            family = LegacyInvoiceClassifier.classify(item)

            if not family:
                result.unsupported.append(item)
                continue

            result.supported_items += 1

            matched = False

            for row in erp_rows:

                if row["name"] in used_rows:
                    continue

                if float(row["amount"]) != float(item["amount"]):
                    continue

                used_rows.add(row["name"])

                result.matches.append(
                    {
                        "erp_row": row["name"],
                        "erp_item": row["item_name"],
                        "type": family,
                        "original_type": item["type"],
                        "relid": item["relid"],
                        "whmcs_invoice_item_id": item["id"],
                        "amount": item["amount"],
                        "confidence": 100,
                        "recoverable": True,
                    }
                )

                matched = True
                break

            if not matched:
                result.unmatched_items += 1

        result.matched_items = len(result.matches)
        result.unsupported_items = len(result.unsupported)

        if result.total_whmcs_items == 0:
            result.status = "EMPTY"

        elif result.supported_items == 0:
            result.status = "UNSUPPORTED"

        elif result.unmatched_items == 0:
            result.status = "RECOVERABLE"

        else:
            result.status = "PARTIAL"

        return result
