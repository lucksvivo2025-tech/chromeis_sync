import traceback

import frappe

from chromeis_sync.migration_audit.missing_invoice_snapshot import (
    MissingInvoiceSnapshot,
)
from chromeis_sync.migration_audit.rebuild import InvoiceRebuilder
from chromeis_sync.migration_audit.models import RepairResult


class MissingInvoiceTransaction:

    def __init__(self, whmcs_invoice_id, target_currency="USD"):

        self.whmcs_invoice_id = int(whmcs_invoice_id)
        self.target_currency = target_currency

    def execute(self):

        savepoint = f"missing_{self.whmcs_invoice_id}"

        print()
        print("=" * 60)
        print(f"WHMCS Invoice : {self.whmcs_invoice_id}")
        print("=" * 60)

        frappe.db.savepoint(savepoint)

        try:

            # --------------------------------------------------
            # Duplicate Protection
            # --------------------------------------------------

            existing = frappe.db.exists(
                "Sales Invoice",
                {
                    "whmcs_invoice_id": str(self.whmcs_invoice_id),
                    "docstatus": ["!=", 2],
                },
            )

            if existing:
                raise Exception(
                    f"WHMCS Invoice {self.whmcs_invoice_id} already exists as {existing}"
                )

            # --------------------------------------------------
            # Create Snapshot
            # --------------------------------------------------

            snapshot = MissingInvoiceSnapshot.create(
                self.whmcs_invoice_id
            )

            if not snapshot["items"]:
                print("✓ Empty WHMCS invoice (no items to migrate)")
                frappe.db.rollback()

                return RepairResult(
                    old_invoice=str(self.whmcs_invoice_id),
                    new_invoice="",
                    success=True,
                    message="Skipped empty invoice",
                )

            # --------------------------------------------------
            # Build Invoice
            # --------------------------------------------------

            rebuilder = InvoiceRebuilder(
                snapshot,
                self.target_currency,
            )

            invoice = rebuilder.build()

            if invoice is None:
                raise Exception(
                    "InvoiceRebuilder.build() returned None."
                )

            # --------------------------------------------------
            # Insert & Submit
            # --------------------------------------------------

            invoice.insert()

            invoice.submit()

            # --------------------------------------------------
            # Verify GL
            # --------------------------------------------------

            gl_count = frappe.db.count(
                "GL Entry",
                {
                    "voucher_no": invoice.name
                }
            )

            # Some historical WHMCS invoices have zero accounting impact
            # (for example, fully settled by customer credit or true zero-value
            # invoices). ERPNext legitimately creates no GL for these.
            if gl_count == 0:

                invoice.reload()

                if abs(float(invoice.base_grand_total or 0)) < 0.01:
                    print("✓ Zero accounting invoice (no GL expected)")
                else:
                    raise Exception(
                        "Invoice submitted but no GL Entries were created."
                    )

            frappe.db.commit()

            print("✓ Invoice Created")
            print(f"✓ Sales Invoice : {invoice.name}")
            print(f"✓ GL Entries    : {gl_count}")
            print("✓ Transaction Committed")

            return RepairResult(
                old_invoice=str(self.whmcs_invoice_id),
                new_invoice=invoice.name,
                success=True,
                message="Created",
            )

        except Exception:

            frappe.db.rollback(save_point=savepoint)

            print("✗ Transaction Rolled Back")

            traceback.print_exc()

            raise
