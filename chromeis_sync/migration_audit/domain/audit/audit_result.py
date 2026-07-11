from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chromeis_sync.migration_audit.domain.matchers.identity_match_result import (
    IdentityMatchResult,
)


@dataclass(slots=True)
class AuditResult:
    """
    Final outcome of auditing one invoice.
    """

    whmcs_invoice_id: int

    erp_invoice_name: str

    success: bool

    identity_result: Optional[IdentityMatchResult] = None

    failure_type: Optional[str] = None

    failure_message: Optional[str] = None
