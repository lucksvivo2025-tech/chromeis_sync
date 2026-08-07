import copy

import frappe


class InvoiceCloner:

    @staticmethod
    def clone(invoice_name):

        source = frappe.get_doc(
            "Sales Invoice",
            invoice_name,
        )

        clone = copy.deepcopy(source)

        #
        # Reset ERP identity
        #

        clone.name = None
        clone.amended_from = None

        clone.creation = None
        clone.modified = None
        clone.modified_by = None
        clone.owner = None
        clone.docstatus = 0
        clone.set_posting_time = 1

        #
        # Child rows become new rows
        #

        for row in clone.items:

            row.name = None
            row.parent = None
            row.parentfield = "items"
            row.parenttype = "Sales Invoice"

        return clone
