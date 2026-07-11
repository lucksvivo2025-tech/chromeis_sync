from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BatchDetail:
    invoice_name: str
    whmcs_invoice_id: Optional[str]
    status: str
    message: str = ""
    new_invoice: Optional[str] = None
    duration: float = 0.0


@dataclass
class MigrationStats:
    processed: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0

    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return round((self.passed / self.processed) * 100, 2)


@dataclass
class BatchResult:
    started_at: datetime
    finished_at: Optional[datetime] = None

    stats: MigrationStats = field(default_factory=MigrationStats)

    details: list[BatchDetail] = field(default_factory=list)

    @property
    def duration(self) -> float:
        if not self.finished_at:
            return 0.0
        return (self.finished_at - self.started_at).total_seconds()

    def add(self, detail: BatchDetail):

        self.details.append(detail)

        self.stats.processed += 1

        if detail.status == "PASS":
            self.stats.passed += 1

        elif detail.status == "FAIL":
            self.stats.failed += 1

        elif detail.status == "SKIPPED":
            self.stats.skipped += 1
