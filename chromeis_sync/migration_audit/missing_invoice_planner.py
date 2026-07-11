from collections import Counter

import frappe

from chromeis_sync.migration_audit.migration_completeness import (
    MigrationCompleteness,
)


class MissingInvoicePlanner:

    def __init__(self):

        self.audit = MigrationCompleteness()

        self.report = self.audit.build()

        self.classify()

    # ---------------------------------------------------------

    def classify(self):

        for row in self.report:

            if row["migration_status"] != "MISSING":
                continue

            invoice_id = row["whmcs_invoice_id"]

            items = frappe.db.sql("""
                SELECT type
                FROM whmcs_mirror.tblinvoiceitems
                WHERE invoiceid=%s
            """, invoice_id, as_dict=True)

            # ---------------------------------------------
            # Empty invoice
            # ---------------------------------------------

            if not items:
                row["migration_status"] = "SKIPPED_EMPTY"
                continue

            # ---------------------------------------------
            # AddFunds invoice
            # ---------------------------------------------

            if all(
                d["type"] == "AddFunds"
                for d in items
            ):
                row["migration_status"] = "ADD_FUNDS"

    # ---------------------------------------------------------

    def plan(self):

        return [
            row
            for row in self.report
            if (
                row["migration_status"] == "MISSING"
                and row["whmcs_status"] == "Paid"
            )
        ]

    # ---------------------------------------------------------

    def statistics(self):

        counter = Counter(
            row["migration_status"]
            for row in self.report
        )

        return {

            "total": len(self.report),

            "migrated": counter.get("MIGRATED", 0),

            "missing": counter.get("MISSING", 0),

            "cancelled": counter.get("CANCELLED", 0),

            "draft": counter.get("DRAFT", 0),

            "empty": counter.get("SKIPPED_EMPTY", 0),

            "add_funds": counter.get("ADD_FUNDS", 0),
        }

    # ---------------------------------------------------------

    def print_summary(self):

        stats = self.statistics()

        print("=" * 60)
        print("Missing Invoice Planner")
        print("=" * 60)

        print(f"Total WHMCS Invoices : {stats['total']}")
        print(f"Migrated             : {stats['migrated']}")
        print(f"Missing              : {stats['missing']}")
        print(f"Cancelled            : {stats['cancelled']}")
        print(f"Draft                : {stats['draft']}")
        print(f"Skipped Empty        : {stats['empty']}")
        print(f"AddFunds             : {stats['add_funds']}")

        print("=" * 60)

    # ---------------------------------------------------------

    def summary(self):

        self.print_summary()

    # ---------------------------------------------------------

    def has_missing(self):

        return len(self.plan()) > 0
