import frappe


class InvoiceIdentityReleaser:

    @staticmethod
    def release(invoice):

        if invoice.docstatus != 2:

            raise Exception(
                "Identity can only be released from cancelled invoices."
            )

        invoice.whmcs_invoice_id = None

        invoice.flags.ignore_validate = True
        invoice.flags.ignore_validate_update_after_submit = True

        invoice.save(
            ignore_permissions=True,
        )

        return invoice
