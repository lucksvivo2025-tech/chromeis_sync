from chromeis_sync.migration_audit.domain.enums.invoice_classification import (
    InvoiceClassification,
)


class InvoiceClassifier:

    def classify(self, invoice):

        if invoice.status == "Paid":

            if invoice.paid_by_credit:
                return InvoiceClassification.PAID_BY_CREDIT

            if invoice.true_zero:
                return InvoiceClassification.TRUE_ZERO

            return InvoiceClassification.PAID

        if invoice.status == "Cancelled":
            return InvoiceClassification.CANCELLED

        if invoice.status == "Unpaid":
            return InvoiceClassification.UNPAID

        if invoice.status == "Collections":
            return InvoiceClassification.COLLECTIONS

        if invoice.status == "Refunded":
            return InvoiceClassification.REFUNDED

        if invoice.status == "Draft":
            return InvoiceClassification.DRAFT

        return InvoiceClassification.UNKNOWN
