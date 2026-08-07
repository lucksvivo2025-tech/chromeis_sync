from collections import Counter

import frappe

from chromeis_sync.sync_engine.framework.migration_quality.quality_engine import (
    MigrationQualityEngine,
)


class FinalMigrationAudit:

    @staticmethod
    def run(limit=None):

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["!=", ""],
            },
            fields=[
                "name",
                "whmcs_invoice_id",
            ],
            order_by="creation asc",
            limit_page_length=limit or 100000,
        )

        status_counter = Counter()
        grade_counter = Counter()

        total_score = 0

        worst = []

        for invoice in invoices:

            result = MigrationQualityEngine.invoice(
                int(invoice.whmcs_invoice_id)
            )

            status_counter[
                result["identity"]["status"]
            ] += 1

            grade_counter[
                result["grade"]
            ] += 1

            total_score += result["score"]

            if result["score"] < 100:

                worst.append(
                    {
                        "invoice": result["invoice"],
                        "erp_invoice": result["erp_invoice"],
                        "grade": result["grade"],
                        "score": result["score"],
                        "deductions": result["deductions"],
                    }
                )

        worst.sort(
            key=lambda x: x["score"]
        )

        return {

            "total_invoices": len(invoices),

            "average_score": round(
                total_score / len(invoices),
                2,
            ) if invoices else 0,

            "identity_statuses": dict(
                sorted(status_counter.items())
            ),

            "grades": dict(
                sorted(grade_counter.items())
            ),

            "worst_25": worst[:25],
        }
