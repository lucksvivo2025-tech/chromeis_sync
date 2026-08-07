from collections import Counter

import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.partial_analyzer import (
    PartialInvoiceAnalyzer,
)


class PartialClassifier:

    @staticmethod
    def analyze(invoice_id):

        result = PartialInvoiceAnalyzer.analyze(
            invoice_id
        )

        counter = Counter()

        for issue in result["issues"]:

            issue_type = issue["type"]

            if issue_type == "UNSUPPORTED":

                item_type = (
                    issue.get("item_type")
                    or "(blank)"
                )

                counter[
                    f"UNSUPPORTED:{item_type}"
                ] += 1

            elif issue_type == "UNMATCHED":

                item_type = (
                    issue.get("item_type")
                    or "(blank)"
                )

                counter[
                    f"UNMATCHED:{item_type}"
                ] += 1

            else:

                counter[issue_type] += 1

        return {
            "invoice": invoice_id,
            "erp_invoice": result["erp_invoice"],
            "status": result["status"],
            "categories": dict(
                sorted(
                    counter.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),
            "issues": result["issues"],
        }

    @staticmethod
    def run(limit=None):

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["!=", ""],
            },
            fields=[
                "whmcs_invoice_id",
            ],
            limit_page_length=limit or 100000,
        )

        summary = Counter()

        total_partial = 0

        for invoice in invoices:

            invoice_id = int(
                invoice.whmcs_invoice_id
            )

            result = PartialInvoiceAnalyzer.analyze(
                invoice_id
            )

            if result["status"] != "PARTIAL":
                continue

            total_partial += 1

            classified = PartialClassifier.analyze(
                invoice_id
            )

            for key, value in classified[
                "categories"
            ].items():

                summary[key] += value

        return {
            "partial_invoices": total_partial,
            "categories": dict(
                sorted(
                    summary.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),
        }
