from chromeis_sync.sync_engine.framework.identity_recovery.legacy_freeform_detector import (
    LegacyFreeformDetector,
)

from chromeis_sync.sync_engine.framework.classification.legacy_invoice_classifier import (
    LegacyInvoiceClassifier,
)

import frappe


class TransformationDetector:

    @staticmethod
    def analyze(invoice_id):

        erp_invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(invoice_id),
            },
            "name",
        )

        if not erp_invoice:
            return {
                "invoice": invoice_id,
                "status": "ERP_MISSING",
            }

        whmcs = frappe.db.sql(
            """
            SELECT
                id,
                type,
                amount,
                description
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
            """,
            (invoice_id,),
            as_dict=True,
        )

        erp = frappe.db.sql(
            """
            SELECT
                name,
                item_name,
                amount
            FROM `tabSales Invoice Item`
            WHERE parent=%s
            ORDER BY idx
            """,
            (erp_invoice,),
            as_dict=True,
        )

        if not whmcs:
            return {
                "invoice": invoice_id,
                "erp_invoice": erp_invoice,
                "status": "EMPTY",
            }

        supported = []
        unsupported = []

        legacy = LegacyFreeformDetector.analyze(
            invoice_id
        )

        if legacy["legacy_freeform"]:

            status = "LEGACY_FREEFORM"

            supported = []
            unsupported = []

            whmcs_total = round(
                sum(float(x["amount"]) for x in whmcs),
                2,
            )

            erp_total = round(
                sum(float(x["amount"]) for x in erp),
                2,
            )

        else:

            for item in whmcs:

                family = LegacyInvoiceClassifier.classify(item)

                if family:
                    supported.append(item)
                else:
                    unsupported.append(item)

            whmcs_total = round(
                sum(float(x["amount"]) for x in whmcs),
                2,
            )

            erp_total = round(
                sum(float(x["amount"]) for x in erp),
                2,
            )

            if (
                len(supported) == len(erp)
                and len(unsupported) == 0
            ):
                status = "IDENTICAL"

            elif (
                len(supported) == len(erp)
                and len(unsupported) > 0
                and whmcs_total == erp_total
            ):
                status = "COLLAPSED"

            elif len(supported) > len(erp):

                if whmcs_total == erp_total:
                    status = "MERGED"
                else:
                    status = "PARTIAL"

            elif len(supported) < len(erp):
                status = "SPLIT"

            else:
                status = "PARTIAL"

        return {
            "invoice": invoice_id,
            "erp_invoice": erp_invoice,
            "status": status,
            "supported_items": len(supported),
            "unsupported_items": len(unsupported),
            "erp_rows": len(erp),
            "whmcs_total": whmcs_total,
            "erp_total": erp_total,
        }
