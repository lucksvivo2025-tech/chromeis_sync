from dataclasses import dataclass, field


@dataclass
class InvoiceAnalysisResult:

    invoice: int
    erp_invoice: str | None = None

    status: str = "UNKNOWN"

    total_whmcs_items: int = 0
    supported_items: int = 0
    unsupported_items: int = 0

    matched_items: int = 0
    unmatched_items: int = 0

    matches: list = field(default_factory=list)
    unsupported: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
