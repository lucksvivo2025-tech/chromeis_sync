from __future__ import annotations

from chromeis_sync.migration_audit.domain.match_results.identity_match_result import (
    IdentityMatchResult,
)
from chromeis_sync.migration_audit.domain.value_objects.business_identity import (
    BusinessIdentity,
)


class IdentityMatcher:
    """
    Compares two BusinessIdentity objects.
    """

    def match(
        self,
        source: BusinessIdentity,
        target: BusinessIdentity,
    ) -> IdentityMatchResult:

        reasons = []

        if source.service_type != target.service_type:
            reasons.append("Different service type")

        if source.operation != target.operation:
            reasons.append("Different operation")

        source_resource = (source.resource_name or "").lower().strip()
        target_resource = (target.resource_name or "").lower().strip()

        if source_resource != target_resource:
            reasons.append("Different resource")

        return IdentityMatchResult(
            matched=len(reasons) == 0,
            confidence=1.0 if len(reasons) == 0 else 0.0,
            reasons=reasons,
        )
