from __future__ import annotations

from enum import Enum
from typing import Optional


class OperationType(str, Enum):
    RENEWAL = "RENEWAL"
    REGISTRATION = "REGISTRATION"
    TRANSFER = "TRANSFER"
    PURCHASE = "PURCHASE"
    UPGRADE = "UPGRADE"
    DOWNGRADE = "DOWNGRADE"
    CANCELLATION = "CANCELLATION"
    UNKNOWN = "UNKNOWN"


class OperationParser:
    """
    Determines the business operation
    represented by an invoice item.

    This parser works on normalized text.
    """

    KEYWORDS = {
        "renew": OperationType.RENEWAL,
        "renewal": OperationType.RENEWAL,

        "register": OperationType.REGISTRATION,
        "registration": OperationType.REGISTRATION,

        "transfer": OperationType.TRANSFER,

        "upgrade": OperationType.UPGRADE,

        "downgrade": OperationType.DOWNGRADE,

        "cancel": OperationType.CANCELLATION,
        "cancellation": OperationType.CANCELLATION,
    }

    def parse(
        self,
        text: str,
    ) -> OperationType:

        text = text.lower()

        for keyword, operation in self.KEYWORDS.items():
            if keyword in text:
                return operation

        return OperationType.PURCHASE
