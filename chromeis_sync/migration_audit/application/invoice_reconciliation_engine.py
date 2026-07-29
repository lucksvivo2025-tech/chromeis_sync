from decimal import Decimal
from collections import Counter

from chromeis_sync.migration_audit.domain.models.invoice import Invoice
from chromeis_sync.migration_audit.domain.classifiers.invoice_classifier import (
    InvoiceClassifier,
)


class InvoiceReconciliationEngine:

    def __init__(self):
        self.classifier = InvoiceClassifier()

    def classify_invoices(self, rows):

        invoices = []

        for row in rows:
            invoices.append(self.build_invoice(row))

        return invoices

    def classification_summary(self, invoices):

        summary = Counter()

        for invoice in invoices:
            summary[invoice.classification.value] += 1

        return dict(summary)

    def expected_erp_statuses(self, invoice):

        classification = invoice.classification

        if classification.name == "PAID":
            return {"Paid"}

        if classification.name == "PAID_BY_CREDIT":
            return {"Paid"}

        if classification.name == "UNPAID":
            return {"Unpaid", "Overdue", "Draft"}

        if classification.name == "COLLECTIONS":
            return {"Overdue"}

        if classification.name == "CANCELLED":
            return {"Cancelled"}

        if classification.name == "REFUNDED":
            return {"Return", "Credit Note Issued", "Cancelled"}

        if classification.name == "DRAFT":
            return {"Draft"}

        if classification.name == "TRUE_ZERO":
            return set()

        return set()

    def build_invoice(self, row):

        invoice = Invoice(
            id=row["id"],
            userid=row["userid"],
            status=row["status"],
            subtotal=Decimal(str(row["subtotal"])),
            credit=Decimal(str(row["credit"])),
            tax=Decimal(str(row["tax"])),
            total=Decimal(str(row["total"])),
        )

        invoice.classification = self.classifier.classify(invoice)

        return invoice
