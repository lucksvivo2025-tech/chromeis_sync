from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ValidationIssue:
    section: str
    field: str
    old: Any
    new: Any

    def __str__(self):
        return (
            f"[{self.section}] "
            f"{self.field}: "
            f"OLD={self.old!r} "
            f"NEW={self.new!r}"
        )


@dataclass
class ValidationResult:
    passed: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)

    def add(
        self,
        section,
        field,
        old,
        new,
    ):
        self.passed = False
        self.issues.append(
            ValidationIssue(
                section,
                field,
                old,
                new,
            )
        )

    def print_summary(self):

        print()

        print("=" * 60)
        print("VALIDATION RESULT")
        print("=" * 60)

        if self.passed:
            print("STATUS : PASS")
            return

        print("STATUS : FAIL")
        print()

        for issue in self.issues:
            print(issue)


class InvoiceValidator:

    HEADER_FIELDS = [

        "customer",
        "customer_name",
        "company",

        "posting_date",
        "posting_time",
        "set_posting_time",
        "due_date",

        "currency",

        "cost_center",

        "remarks",

        "custom_whmcs_client_id",
        "whmcs_invoice_id",
    ]

    def __init__(
        self,
        old_snapshot: Dict,
        new_snapshot: Dict,
    ):

        self.old = old_snapshot
        self.new = new_snapshot

        self.result = ValidationResult()

    def validate_header(self):

        old = self.old["header"]
        new = self.new["header"]

        for field in self.HEADER_FIELDS:

            old_value = old.get(field)
            new_value = new.get(field)

            if old_value != new_value:

                self.result.add(
                    "HEADER",
                    field,
                    old_value,
                    new_value,
                )

    def validate_items(self):

        old_items = self.old["items"]
        new_items = self.new["items"]

        if len(old_items) != len(new_items):
            self.result.add(
                "ITEMS",
                "count",
                len(old_items),
                len(new_items),
            )
            return

        fields = [
            "item_code",
            "item_name",
            "qty",
            "rate",
            "amount",
            "income_account",
        ]

        for index, (old, new) in enumerate(zip(old_items, new_items), start=1):

            for field in fields:

                if old.get(field) != new.get(field):
                    self.result.add(
                        f"ITEM {index}",
                        field,
                        old.get(field),
                        new.get(field),
                    )

    def validate(self):

        self.validate_header()
        self.validate_items()

        return self.result
