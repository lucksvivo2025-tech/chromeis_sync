from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ParserResult(Generic[T]):
    """
    Generic parser result.

    Every parser in the migration framework
    returns this object.

    Examples

    ParserResult[OperationType]
    ParserResult[str]
    ParserResult[BillingCycle]
    """

    value: Optional[T]

    confidence: float

    strategy: str

    matched_text: Optional[str] = None
