from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class BusinessIdentity:
    """
    Canonical business identity of an invoice item.

    This object is produced after normalization and
    is used by the ItemMatcher.

    It is intentionally independent of ERPNext
    and WHMCS implementations.
    """

    service_type: Optional[str] = None

    operation: Optional[str] = None

    resource_name: Optional[str] = None

    billing_cycle: Optional[str] = None

    period_start: Optional[str] = None

    period_end: Optional[str] = None

    amount_signature: Optional[str] = None
