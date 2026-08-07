from dataclasses import dataclass


@dataclass
class ClassificationResult:

    category: str

    reason: str = ""

    action: str = ""
