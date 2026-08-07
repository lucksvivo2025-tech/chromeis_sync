from collections import Counter

import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)


class TransformationStatistics:

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

        samples = {}

        total = 0

        for invoice in invoices:

            invoice_id = int(invoice.whmcs_invoice_id)

            try:

                result = TransformationDetector.analyze(
                    invoice_id
                )

                status = result["status"]

            except Exception:

                status = "ERROR"

                result = {
                    "erp_invoice": invoice.name,
                }

            total += 1

            status_counter[status] += 1

            if (
                status != "IDENTICAL"
                and status not in samples
            ):

                samples[status] = {
                    "invoice": invoice_id,
                    "erp_invoice": result.get(
                        "erp_invoice"
                    ),
                }

        return {

            "total_invoices": total,

            "statuses": dict(
                sorted(
                    status_counter.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),

            "samples": samples,
        }
