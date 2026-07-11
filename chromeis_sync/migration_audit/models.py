from dataclasses import dataclass, field


@dataclass
class ManifestRow:
    invoice_name: str
    whmcs_invoice_id: str
    customer: str
    erp_currency: str
    target_currency: str
    grand_total: float
    item_count: int


@dataclass
class VerificationResult:
    passed: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class RepairResult:
    old_invoice: str
    new_invoice: str = ""
    success: bool = False
    message: str = ""

@dataclass
class RepairCandidate:
    invoice_name: str
    whmcs_invoice_id: str

    # OK | INFO | SKIP | REPAIR
    status: str = "OK"

    reasons: list = field(default_factory=list)

    currency: str = ""
    target_currency: str = ""

    submitted: bool = False
    has_gl: bool = False

    conversion_rate: float = 0.0

    repair_required: bool = False

    # True when missing GL is an expected accounting outcome
    expected_no_gl: bool = False
