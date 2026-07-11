from __future__ import annotations

from dataclasses import dataclass

from chromeis_sync.migration_audit.domain.value_objects.business_identity import (
    BusinessIdentity,
)


@dataclass(slots=True)
class BenchmarkResult:
    """
    Result of running IdentityExtractor
    against a single invoice line.
    """

    invoice_id: int | None

    description: str

    identity: BusinessIdentity

    success: bool

    notes: str = ""
