from enum import Enum


class InvoiceClassification(Enum):
    PAID = "Paid"

    PAID_BY_CREDIT = "Paid by Credit"

    TRUE_ZERO = "True Zero"

    CANCELLED = "Cancelled"

    UNPAID = "Unpaid"

    COLLECTIONS = "Collections"

    REFUNDED = "Refunded"

    DRAFT = "Draft"

    UNKNOWN = "Unknown"
