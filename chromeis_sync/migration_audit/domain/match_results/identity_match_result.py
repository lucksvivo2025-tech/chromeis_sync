from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class IdentityMatchResult:
    matched: bool

    confidence: float

    reasons: list[str] = field(default_factory=list)
