from dataclasses import dataclass


@dataclass
class ValidationResult:

    valid: bool

    code: str = ""

    severity: str = "INFO"

    reason: str = ""
