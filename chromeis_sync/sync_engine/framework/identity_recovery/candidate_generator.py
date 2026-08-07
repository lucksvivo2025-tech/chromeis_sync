import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)


class CandidateGenerator:

    @staticmethod
    def generate(invoice_id):

        recovery = IdentityRecoveryEngine.invoice(
            invoice_id,
        )

        analysis = recovery["analysis"]

        erp_invoice = analysis.erp_invoice

        if not erp_invoice:

            return {
                "invoice": invoice_id,
                "status": "ERP_MISSING",
                "candidates": [],
            }

        erp_rows = frappe.db.sql(
            """
            SELECT
                name,
                idx,
                item_code,
                item_name,
                amount,
                custom_whmcs_service_id,
                custom_whmcs_domain_id,
                custom_whmcs_addon_id
            FROM `tabSales Invoice Item`
            WHERE parent=%s
            ORDER BY idx
            """,
            (erp_invoice,),
            as_dict=True,
        )

        candidates = []

        for item in analysis.unsupported:

            possible = []

            for row in erp_rows:

                confidence = 0
                reasons = []

                if abs(float(item["amount"]) - float(row["amount"])) < 0.01:
                    confidence += 40
                    reasons.append("Amount")

                if row.get("item_name"):

                    text = row["item_name"].lower()

                    for word in item["description"].lower().split():

                        if len(word) > 3 and word in text:
                            confidence += 5

                if confidence > 0:

                    possible.append(
                        {
                            "erp_row": row["name"],
                            "idx": row["idx"],
                            "confidence": confidence,
                            "reason": ", ".join(reasons),
                        }
                    )

            possible.sort(
                key=lambda x: x["confidence"],
                reverse=True,
            )

            candidates.append(
                {
                    "whmcs_item": item["id"],
                    "description": item["description"],
                    "amount": float(item["amount"]),
                    "erp_candidates": possible,
                }
            )

        return {
            "invoice": invoice_id,
            "erp_invoice": erp_invoice,
            "identity_status": analysis.status,
            "supported_items": analysis.supported_items,
            "unsupported_items": analysis.unsupported_items,
            "erp_rows": len(erp_rows),
            "candidates": candidates,
        }
