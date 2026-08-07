from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from .status import SyncStatus


@dataclass
class IdentityResult:

    # Identity
    status: SyncStatus

    doctype: Optional[str] = None
    document_name: Optional[str] = None

    whmcs_id: Optional[str] = None
    erp_id: Optional[str] = None

    # Resolution
    reason: str = ""
    confidence: int = 100

    # Multiple possible matches
    matches: List[str] = field(default_factory=list)

    # ERP snapshot returned by repository
    data: Dict[str, Any] = field(default_factory=dict)

    # Validation / Audit
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def found(self):
        return self.status == SyncStatus.MATCHED
