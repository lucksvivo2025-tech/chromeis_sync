from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------
# Migration Status
# ---------------------------------------------------------

class MigrationStatus(str, Enum):

    PENDING = "pending"

    RUNNING = "running"

    SUCCESS = "success"

    FAILED = "failed"

    SKIPPED = "skipped"


# ---------------------------------------------------------
# Migration Options
# ---------------------------------------------------------

@dataclass(slots=True)
class MigrationOptions:

    target_currency: str

    dry_run: bool = False

    auto_commit: bool = False

    stop_on_error: bool = True

    batch_size: int = 100


# ---------------------------------------------------------
# Migration Context
# ---------------------------------------------------------

@dataclass(slots=True)
class MigrationContext:

    invoice_name: str

    started_at: datetime

    options: MigrationOptions

    whmcs_invoice_id: Optional[int] = None


# ---------------------------------------------------------
# Invoice Migration Result
# ---------------------------------------------------------

@dataclass(slots=True)
class MigrationResult:

    invoice_name: str

    new_invoice_name: Optional[str]

    status: MigrationStatus

    message: Optional[str] = None

    duration_seconds: float = 0.0


# ---------------------------------------------------------
# Batch Statistics
# ---------------------------------------------------------

@dataclass(slots=True)
class MigrationStatistics:

    processed: int = 0

    passed: int = 0

    failed: int = 0

    skipped: int = 0


# ---------------------------------------------------------
# Batch Result
# ---------------------------------------------------------

@dataclass(slots=True)
class MigrationBatchResult:

    started_at: datetime

    finished_at: Optional[datetime] = None

    statistics: MigrationStatistics = field(default_factory=MigrationStatistics)

    results: List[MigrationResult] = field(default_factory=list)
