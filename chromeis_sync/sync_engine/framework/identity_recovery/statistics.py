from collections import Counter

import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.engine import (
    IdentityRecoveryEngine,
)


class IdentityRecoveryStatistics:

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

        supported_type_counter = Counter()
        unsupported_type_counter = Counter()
        all_type_counter = Counter()

        total = 0

        for invoice in invoices:

            invoice_id = int(invoice.whmcs_invoice_id)

            result = IdentityRecoveryEngine.invoice(
                invoice_id,
                commit=False,
            )

            analysis = result["analysis"]

            total += 1

            status_counter[analysis.status] += 1

            #
            # matched/supported
            #

            for match in analysis.matches:

                original = (
                    match["original_type"]
                    or "(blank)"
                )

                classified = match["type"]

                supported_type_counter[
                    classified
                ] += 1

                all_type_counter[
                    classified
                ] += 1

                if (
                    original == "(blank)"
                    and classified != "(blank)"
                ):

                    supported_type_counter[
                        "Legacy→" + classified
                    ] += 1
            #
            # unsupported items
            #

            if hasattr(
                analysis,
                "unsupported",
            ):

                for item in analysis.unsupported:

                    original = (
                        item["type"]
                        or "(blank)"
                    )

                    unsupported_type_counter[
                        original
                    ] += 1

                    all_type_counter[
                        original
                    ] += 1

        return {

            "total_invoices": total,

            "statuses": dict(
                sorted(status_counter.items())
            ),

            "supported_types": dict(
                sorted(
                    supported_type_counter.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),

            "unsupported_types": dict(
                sorted(
                    unsupported_type_counter.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),

            "all_types": dict(
                sorted(
                    all_type_counter.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),
        }
