import traceback

import frappe

from chromeis_sync.migration_audit.snapshot import SnapshotService
from chromeis_sync.migration_audit.repair import InvoiceRepair
from chromeis_sync.migration_audit.rebuild import InvoiceRebuilder
from chromeis_sync.migration_audit.verify import InvoiceVerifier
from chromeis_sync.migration_audit.gl_verify import GLVerifier
from chromeis_sync.migration_audit.models import RepairResult


class InvoiceTransaction:

    def __init__(self, invoice_name, target_currency):
        self.invoice_name = invoice_name
        self.target_currency = target_currency

    def execute(self):

        savepoint = self.invoice_name.replace("-", "_")

        print(f"\n===== {self.invoice_name} =====")

        snapshot = SnapshotService.create(self.invoice_name)

        frappe.db.savepoint(savepoint)

        try:

            # -------------------------
            # Cancel original invoice
            # -------------------------

            repair = InvoiceRepair(self.invoice_name)

            if repair.invoice.docstatus == 1:
                repair.cancel()
                repair.release_whmcs_id()

            # -------------------------
            # Build replacement invoice
            # -------------------------

            rebuilder = InvoiceRebuilder(
                snapshot,
                self.target_currency,
            )

            new_invoice = rebuilder.build()

            # Restore original WHMCS Invoice ID
            if snapshot["header"].get("whmcs_invoice_id"):
                new_invoice.whmcs_invoice_id = snapshot["header"]["whmcs_invoice_id"]

            # -------------------------
            # Insert & Submit
            # -------------------------

            new_invoice.insert()
            new_invoice.submit()

            # -------------------------
            # Verify Invoice
            # -------------------------

            invoice_result = InvoiceVerifier().verify(
                snapshot,
                new_invoice,
                self.target_currency,
            )

            if not invoice_result.passed:
                raise Exception(
                    "\n".join(invoice_result.errors)
                )

            print("✓ Invoice Verification Passed")

            # -------------------------
            # Verify GL
            # -------------------------

            gl_result = GLVerifier().verify(
                snapshot,
                new_invoice,
            )

            if not gl_result.passed:
                raise Exception(
                    "\n".join(gl_result.errors)
                )

            print("✓ GL Verification Passed")

            frappe.db.commit()

            print("✓ Transaction Committed")

            return RepairResult(
                old_invoice=self.invoice_name,
                new_invoice=new_invoice.name,
                success=True,
                message="Verified",
            )

        except Exception:

            frappe.db.rollback(save_point=savepoint)

            print("✗ Transaction Rolled Back")

            traceback.print_exc()

            raise
