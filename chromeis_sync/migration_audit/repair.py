import frappe


class InvoiceRepair:

    def __init__(self, invoice_name):

        self.invoice_name = invoice_name
        self.invoice = frappe.get_doc(
            "Sales Invoice",
            invoice_name
        )

    def cancel(self):

        if self.invoice.docstatus != 1:
            raise Exception(
                f"{self.invoice.name} is not submitted."
            )

        self.invoice.cancel()

        self.invoice.reload()

        if self.invoice.docstatus != 2:
            raise Exception(
                "Cancel failed."
            )

        print("✓ Cancelled")

    def release_whmcs_id(self):

        frappe.db.set_value(
            "Sales Invoice",
            self.invoice.name,
            "whmcs_invoice_id",
            None,
            update_modified=False
        )

        value = frappe.db.get_value(
            "Sales Invoice",
            self.invoice.name,
            "whmcs_invoice_id"
        )

        if value is not None:
            raise Exception(
                "WHMCS Invoice ID still exists."
            )

        print("✓ WHMCS ID Released")
