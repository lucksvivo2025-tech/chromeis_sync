import traceback

import frappe

from chromeis_sync.migration_audit.snapshot import SnapshotService
from chromeis_sync.migration_audit.repair import InvoiceRepair
from chromeis_sync.migration_audit.rebuild import InvoiceRebuilder
from chromeis_sync.migration_audit.commercial_verify import CommercialVerifier
from chromeis_sync.migration_audit.commercial_gl_verify import CommercialGLVerifier
from chromeis_sync.migration_audit.models import RepairResult


class InvoiceTransaction:

    def __init__(self, invoice_name, target_currency=None):
        self.invoice_name = invoice_name
        self.target_currency = target_currency

    def execute(self):
        try:
            print(f"\n===== {self.invoice_name} =====")

            # -------------------------
            # Load invoice
            # -------------------------
            old_invoice = frappe.get_doc(
                "Sales Invoice",
                self.invoice_name,
            )

            if old_invoice.docstatus != 1:
                raise Exception(
                    f"{self.invoice_name} is not a submitted invoice."
                )

            # Auto-detect currency if not provided
            if self.target_currency is None:
                self.target_currency = old_invoice.currency

            # -------------------------
            # Snapshot
            # -------------------------
            snapshot = SnapshotService.create(
                self.invoice_name
            )

            # -------------------------
            # Cancel original invoice
            # -------------------------
            old_invoice.cancel()

            print("✓ Cancelled")

            # -------------------------
            # Release WHMCS Invoice ID
            # -------------------------
            if old_invoice.whmcs_invoice_id:
                old_invoice.db_set(
                    "whmcs_invoice_id",
                    None,
                    update_modified=False,
                )

            print("✓ WHMCS ID Released")

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

            # ==========================================================
            # DEBUG BEFORE INSERT
            # ==========================================================
            print("\n==============================")
            print("BEFORE INSERT")
            print("==============================")
            print("paid_amount       :", new_invoice.paid_amount)
            print("outstanding_amount:", new_invoice.outstanding_amount)
            print("status            :", new_invoice.status)
            print("grand_total       :", new_invoice.grand_total)

            # -------------------------
            # Insert
            # -------------------------
            new_invoice.insert()
            new_invoice.reload()

            print("\n==============================")
            print("AFTER INSERT")
            print("==============================")
            print("paid_amount       :", new_invoice.paid_amount)
            print("outstanding_amount:", new_invoice.outstanding_amount)
            print("status            :", new_invoice.status)
            print("grand_total       :", new_invoice.grand_total)

            # -------------------------
            # Submit
            # -------------------------
            new_invoice.submit()
            new_invoice.reload()

            print("\n==============================")
            print("AFTER SUBMIT")
            print("==============================")
            print("paid_amount       :", new_invoice.paid_amount)
            print("outstanding_amount:", new_invoice.outstanding_amount)
            print("status            :", new_invoice.status)
            print("grand_total       :", new_invoice.grand_total)

            # -------------------------
            # Verify Invoice
            # -------------------------
            invoice_result = CommercialVerifier().verify(
                snapshot,
                new_invoice,
                self.target_currency,
            )

            if not invoice_result.passed:
                raise Exception("\n".join(invoice_result.errors))

            print("✓ Invoice Verification Passed")

            # -------------------------
            # Verify GL
            # -------------------------
            gl_result = CommercialGLVerifier().verify(
                snapshot,
                new_invoice,
            )

            if not gl_result.passed:
                raise Exception("\n".join(gl_result.errors))

            print("✓ GL Verification Passed")

            # -------------------------
            # Commit
            # -------------------------
            frappe.db.commit()

            print("✓ Transaction Committed")

            return RepairResult(
                old_invoice=self.invoice_name,
                new_invoice=new_invoice.name,
                success=True,
                message="Verified",
            )

        except Exception:
            frappe.db.rollback()
            print("✗ Transaction Rolled Back")
            traceback.print_exc()
            raise
