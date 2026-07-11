import frappe

from chromeis_sync.migration_audit.snapshot import SnapshotService
from chromeis_sync.migration_audit.rebuild import InvoiceRebuilder


class InvoiceMigrator:

    def __init__(self, invoice_name, target_currency=None):
        self.invoice_name = invoice_name
        self.target_currency = target_currency

        self.snapshot = None
        self.old_invoice = None
        self.new_invoice = None
        self.rebuilder = None

        # Preserve the original unique WHMCS invoice id
        self.original_whmcs_invoice_id = None

    def take_snapshot(self):
        self.snapshot = SnapshotService.create(self.invoice_name)

        if not self.target_currency:
            self.target_currency = self.snapshot["header"]["currency"]

    def load_old_invoice(self):
        self.old_invoice = frappe.get_doc(
            "Sales Invoice",
            self.invoice_name
        )

        # Save before we release it
        self.original_whmcs_invoice_id = self.old_invoice.whmcs_invoice_id

    def cancel_old_invoice(self):
        if self.old_invoice.docstatus == 1:
            self.old_invoice.cancel()

    def release_whmcs_id(self):
        frappe.db.set_value(
            "Sales Invoice",
            self.old_invoice.name,
            "whmcs_invoice_id",
            None,
            update_modified=False
        )

    def build_new_invoice(self):
        self.rebuilder = InvoiceRebuilder(
            self.snapshot,
            self.target_currency
        )

        self.new_invoice = self.rebuilder.build()

        # Restore the original WHMCS invoice id
        self.new_invoice.whmcs_invoice_id = self.original_whmcs_invoice_id

    def insert_new_invoice(self):
        self.new_invoice.flags.ignore_permissions = True
        self.new_invoice.insert()

    def submit_new_invoice(self):
        self.new_invoice.submit()

    def run(self, dry_run=True):

        self.take_snapshot()

        self.load_old_invoice()

        self.cancel_old_invoice()

        self.release_whmcs_id()

        self.build_new_invoice()

        self.insert_new_invoice()

        self.submit_new_invoice()

        if dry_run:
            frappe.db.rollback()
        else:
            frappe.db.commit()

        return self.new_invoice
