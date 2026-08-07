from dataclasses import dataclass
from typing import Optional


@dataclass
class UpsertResult:
    """
    Result of an ERP upsert operation.
    """

    success: bool

    action: str

    doctype: str

    document_name: Optional[str] = None

    message: str = ""

    @property
    def created(self):
        return self.action == "created"

    @property
    def updated(self):
        return self.action == "updated"

    @property
    def skipped(self):
        return self.action == "skipped"
