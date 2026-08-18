import frappe

from chromeis_sync.level5.classification.candidate_classifier import (
    ERPCandidate,
)


class ERPCandidateCollector:

    @staticmethod
    def sales_invoice(whmcs_invoice_id):

        rows = frappe.db.sql(
            """
            SELECT
                name,
                docstatus,
                status,
                posting_date,
                grand_total,
                whmcs_invoice_id
            FROM `tabSales Invoice`
            WHERE whmcs_invoice_id=%s
            ORDER BY
                docstatus ASC,
                posting_date ASC,
                name ASC
            """,
            (str(whmcs_invoice_id),),
            as_dict=True,
        )

        candidates = []

        for row in rows:
            candidates.append(
                ERPCandidate(
                    erp_id=row["name"],
                    doctype="Sales Invoice",
                    docstatus=row["docstatus"],
                    status=row["status"],
                    evidence={
                        "posting_date": str(row["posting_date"]),
                        "grand_total": float(
                            row["grand_total"] or 0
                        ),
                        "whmcs_invoice_id": str(
                            row["whmcs_invoice_id"]
                        ),
                    },
                )
            )

        return candidates
