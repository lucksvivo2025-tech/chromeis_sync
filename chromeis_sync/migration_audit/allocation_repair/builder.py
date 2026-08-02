import frappe


class PaymentReferenceBuilder:
    """
    Builds the Payment Entry Reference dictionary
    exactly as ERPNext does.

    This class performs NO database writes.
    """

    def build(self, payment_entry, sales_invoice):

        return {
            "reference_doctype": "Sales Invoice",
            "reference_name": sales_invoice.name,
            "bill_no": sales_invoice.get("bill_no"),
            "due_date": sales_invoice.get("due_date"),
            "total_amount": sales_invoice.grand_total,
            "outstanding_amount": sales_invoice.outstanding_amount,
            "allocated_amount": min(
                float(payment_entry.paid_amount),
                float(sales_invoice.grand_total),
            ),
        }
