from dataclasses import dataclass, field


@dataclass
class PaymentReconciliationCandidate:
    # WHMCS (Source of Truth)
    whmcs_account_id: int
    whmcs_invoice_id: int
    whmcs_transaction_id: str
    whmcs_customer_id: int
    whmcs_payment_date: str
    whmcs_amount: float
    whmcs_refund_amount: float

    # ERP
    payment_entry: str | None
    expected_sales_invoice: str | None
    allocated_sales_invoice: str | None
    customer: str | None

    paid_amount: float = 0.0
    unallocated_amount: float = 0.0
    outstanding_amount: float = 0.0

    reference_count: int = 0

    status: str = "PENDING"

    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class PaymentReconciliationResult:
    total: int = 0

    passed: int = 0
    failed: int = 0

    missing_payment_entry: int = 0
    missing_sales_invoice: int = 0

    customer_mismatch: int = 0
    amount_mismatch: int = 0

    missing_allocation: int = 0

    refunds: int = 0
    cancelled: int = 0

    warnings: int = 0
