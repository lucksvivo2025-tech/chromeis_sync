import frappe


class InvoiceMutator:

    @staticmethod
    def load(invoice_name):

        return frappe.get_doc(
            "Sales Invoice",
            invoice_name,
        )

    @staticmethod
    def ensure_draft(invoice):

        if invoice.docstatus == 0:
            return

        if invoice.docstatus == 1:

            raise Exception(
                f"Invoice {invoice.name} is Submitted."
            )

        if invoice.docstatus == 2:

            raise Exception(
                f"Invoice {invoice.name} is Cancelled."
            )

        raise Exception(
            f"Unknown docstatus {invoice.docstatus}"
        )

    @staticmethod
    def delete_all_rows(invoice):

        invoice.items = []

    @staticmethod
    def add_row(invoice, row):

        invoice.append(
            "items",
            {
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "description": row["description"],
                "qty": row["qty"],
                "rate": row["rate"],
                "amount": row["amount"],
                "income_account": row["income_account"],
            },
        )

    @staticmethod
    def recalculate(invoice):

        invoice.set_missing_values()
        invoice.calculate_taxes_and_totals()

    @staticmethod
    def save(invoice):

        invoice.flags.ignore_validate_update_after_submit = True

        invoice.save(
            ignore_permissions=True,
        )

    @staticmethod
    def commit():

        frappe.db.commit()
