from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------
# Validation Severity
# ---------------------------------------------------------

class ValidationSeverity(str, Enum):

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"


# ---------------------------------------------------------
# Validation Issue
# ---------------------------------------------------------

@dataclass(slots=True)
class ValidationIssue:

    component: str

    field: str

    expected: object

    actual: object

    severity: ValidationSeverity = ValidationSeverity.ERROR

    message: Optional[str] = None


# ---------------------------------------------------------
# Validation Result
# ---------------------------------------------------------

@dataclass(slots=True)
class ValidationResult:

    passed: bool = True

    issues: List[ValidationIssue] = field(default_factory=list)

    def add(self, issue: ValidationIssue):

        self.issues.append(issue)

        if issue.severity == ValidationSeverity.ERROR:
            self.passed = False


# ---------------------------------------------------------
# Accounting Difference
# ---------------------------------------------------------

@dataclass(slots=True)
class AccountingDifference:

    account: str

    cost_center: Optional[str]

    expected_debit: float

    actual_debit: float

    expected_credit: float

    actual_credit: float


# ---------------------------------------------------------
# Accounting Verification Result
# ---------------------------------------------------------

@dataclass(slots=True)
class AccountingVerificationResult:

    passed: bool = True

    differences: List[AccountingDifference] = field(default_factory=list)
