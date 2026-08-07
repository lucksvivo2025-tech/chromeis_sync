import frappe

from chromeis_sync.sync_engine.framework.classification.legacy_invoice_classifier import (
    LegacyInvoiceClassifier,
)


class LegacyFreeformDetector:

    @staticmethod
    def analyze(invoice_id):

        rows = frappe.db.sql(
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

        if not rows:

            return {
                "invoice": invoice_id,
                "status": "NOT_FOUND",
                "rows": 0,
                "blank_types": 0,
                "zero_relids": 0,
                "supported_items": 0,
                "legacy_freeform": False,
            }

        blank_types = 0
        zero_relids = 0
        supported_items = 0

        for row in rows:

            if not (row["type"] or "").strip():
                blank_types += 1

            if int(row["relid"] or 0) == 0:
                zero_relids += 1

            if LegacyInvoiceClassifier.classify(row):
                supported_items += 1

        legacy = (
            blank_types == len(rows)
            and zero_relids == len(rows)
            and supported_items == 0
        )

        return {

            "invoice": invoice_id,

            "rows": len(rows),

            "blank_types": blank_types,

            "zero_relids": zero_relids,

            "supported_items": supported_items,

            "legacy_freeform": legacy,

            "status": (
                "LEGACY_FREEFORM"
                if legacy
                else "NORMAL"
            ),
        }
