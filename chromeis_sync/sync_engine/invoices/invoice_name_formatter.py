import frappe


class InvoiceNameFormatter:

    @staticmethod
    def format(invoice):

        if not invoice.name:
            raise Exception("Invoice has no ERP name.")

        if not getattr(invoice, "whmcs_invoice_id", None):
            raise Exception("WHMCS Invoice ID missing.")

        parts = invoice.name.split("-")

        if len(parts) < 4:
            raise Exception(
                f"Unexpected ERP invoice name: {invoice.name}"
            )

        if parts[-1].startswith("W"):
            return invoice.name

        return (
            f"{invoice.name}"
            f"-W{invoice.whmcs_invoice_id}"
        )

    @staticmethod
    def rename(invoice):

        new_name = InvoiceNameFormatter.format(invoice)

        if new_name == invoice.name:
            return invoice.name

        frappe.rename_doc(
            "Sales Invoice",
            invoice.name,
            new_name,
            force=True,
            merge=False,
        )

        return new_name
