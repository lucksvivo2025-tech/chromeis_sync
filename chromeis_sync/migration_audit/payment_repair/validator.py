import frappe


class PaymentRepairValidator:

    def validate(self, row):

        errors = []

        # --------------------------------------------------
        # Payment Entry
        # --------------------------------------------------

        pe = frappe.db.get_value(
            "Payment Entry",
            row.payment_entry,
            [
                "docstatus",
                "party",
                "paid_amount",
                "unallocated_amount",
            ],
            as_dict=True,
        )

        if not pe:
            errors.append("Payment Entry missing")
            return errors

        if pe.docstatus != 1:
            errors.append("Payment Entry not submitted")

        if pe.party != row.customer:
            errors.append("Customer mismatch")

        if float(pe.paid_amount) != float(row.paid_amount):
            errors.append("Amount mismatch")

        refs = frappe.db.count(
            "Payment Entry Reference",
            {
                "parent": row.payment_entry
            }
        )

        if refs:
            errors.append("Already has references")

        if row.reference_count > 0:
            errors.append("Already has references")

        if not row.sales_invoice:
            errors.append("Sales Invoice missing")

        si = frappe.db.get_value(
            "Sales Invoice",
            row.sales_invoice,
            ["docstatus"],
            as_dict=True,
        )

        if not si:
            errors.append("Sales Invoice missing")
        elif si.docstatus == 2:
            errors.append("Sales Invoice cancelled")

        return errors
