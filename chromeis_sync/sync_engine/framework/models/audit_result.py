from dataclasses import dataclass

from .status import SyncStatus


@dataclass
class AuditResult:

    status: SyncStatus

    category: str = ""

    message: str = ""

    reference: str = ""
