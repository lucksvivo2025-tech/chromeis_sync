from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from chromeis_sync.migration_audit.models.snapshot import SnapshotInvoice, SnapshotItem
from chromeis_sync.migration_audit.models.whmcs import WHMCSInvoice, WHMCSItem


# ---------------------------------------------------------
# Match Strategy
# ---------------------------------------------------------

class MatchStrategy(str, Enum):

    EXACT_METADATA = "exact_metadata"

    BUSINESS_IDENTITY = "business_identity"

    DESCRIPTION_AMOUNT = "description_amount"

    FUZZY = "fuzzy"

    MANUAL_REVIEW = "manual_review"


# ---------------------------------------------------------
# Match Status
# ---------------------------------------------------------

class MatchStatus(str, Enum):

    MATCHED = "matched"

    REVIEW_REQUIRED = "review_required"

    UNMATCHED = "unmatched"


# ---------------------------------------------------------
# Item Match
# ---------------------------------------------------------

@dataclass(slots=True)
class MatchedItem:

    snapshot_items: List[SnapshotItem] = field(default_factory=list)

    whmcs_items: List[WHMCSItem] = field(default_factory=list)

    strategy: MatchStrategy = MatchStrategy.MANUAL_REVIEW

    confidence: float = 0.0

    status: MatchStatus = MatchStatus.UNMATCHED

    reason: Optional[str] = None


# ---------------------------------------------------------
# Invoice Match
# ---------------------------------------------------------

@dataclass(slots=True)
class MatchedInvoice:

    snapshot: SnapshotInvoice

    whmcs: WHMCSInvoice

    items: List[MatchedItem] = field(default_factory=list)

    overall_confidence: float = 0.0

    review_required: bool = False
