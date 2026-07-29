"""
Base Report Class

Every reconciliation report inherits from this class.
"""

from abc import ABC, abstractmethod
from datetime import datetime

import frappe


class BaseReport(ABC):

    report_id = "BASE"
    report_name = "Base Report"

    def __init__(self):

        self.started = None
        self.finished = None

        # JSON result returned by execute()
        self.results = []

        # Audit status
        self.pass_count = 0
        self.warn_count = 0
        self.fail_count = 0

        # Exception collection
        self.exceptions = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        self.started = datetime.now()

    def finish(self):
        self.finished = datetime.now()

    # ------------------------------------------------------------------
    # Database Helpers
    # ------------------------------------------------------------------

    def scalar(self, sql):
        """Return first value from SQL."""
        value = frappe.db.sql(sql)

        if not value:
            return None

        return value[0][0]

    def rows(self, sql):
        """Return rows as dict."""
        return frappe.db.sql(sql, as_dict=True)

    # ------------------------------------------------------------------
    # Result Recording
    # ------------------------------------------------------------------

    def add_result(
        self,
        metric,
        whmcs=None,
        erp=None,
        status=None,
        notes=None,
    ):

        difference = None

        if (
            whmcs is not None
            and erp is not None
            and isinstance(whmcs, (int, float))
            and isinstance(erp, (int, float))
        ):
            difference = whmcs - erp

            if status is None:
                status = "PASS" if difference == 0 else "FAIL"

        if status is None:
            status = "INFO"

        if status == "PASS":
            self.pass_count += 1

        elif status == "WARN":
            self.warn_count += 1

        elif status == "FAIL":
            self.fail_count += 1

        self.results.append({
            "metric": metric,
            "whmcs": whmcs,
            "erp": erp,
            "difference": difference,
            "status": status,
            "notes": notes,
        })

    # ------------------------------------------------------------------
    # Comparison Helper
    # ------------------------------------------------------------------

    def compare(self, metric, whmcs_sql, erp_sql):

        whmcs = self.scalar(whmcs_sql)
        erp = self.scalar(erp_sql)

        status = "PASS" if whmcs == erp else "FAIL"

        self.add_result(
            metric=metric,
            whmcs=whmcs,
            erp=erp,
            status=status,
        )

        print(
            f"{metric:<35}"
            f"WHMCS={str(whmcs):<10}"
            f"ERP={str(erp):<10}"
            f"{status}"
        )

    # ------------------------------------------------------------------
    # Summary Helper
    # ------------------------------------------------------------------

    def info(self, metric, value):

        self.add_result(
            metric=metric,
            whmcs=value,
            status="INFO",
        )

        print(f"{metric:<40}{value}")

    # ------------------------------------------------------------------
    # Audit Helpers
    # ------------------------------------------------------------------

    def pass_check(self, metric, notes=None):

        self.add_result(
            metric=metric,
            status="PASS",
            notes=notes,
        )

        print(f"{metric:<40}PASS")

    def warn_check(self, metric, notes=None):

        self.add_result(
            metric=metric,
            status="WARN",
            notes=notes,
        )

        print(f"{metric:<40}WARN")

    def fail_check(self, metric, notes=None):

        self.add_result(
            metric=metric,
            status="FAIL",
            notes=notes,
        )

        print(f"{metric:<40}FAIL")

    # ------------------------------------------------------------------
    # Exception Recording
    # ------------------------------------------------------------------

    def add_exception(self, category, **kwargs):

        record = {
            "category": category
        }

        record.update(kwargs)

        self.exceptions.append(record)

    # ------------------------------------------------------------------
    # Final Summary
    # ------------------------------------------------------------------

    def print_audit_summary(self):

        print("\n====================================================")
        print("AUDIT SUMMARY")
        print("====================================================\n")

        print(f"PASS : {self.pass_count}")
        print(f"WARN : {self.warn_count}")
        print(f"FAIL : {self.fail_count}")

        if self.fail_count == 0:
            overall = "PASS"

        elif self.warn_count > 0:
            overall = "WARN"

        else:
            overall = "FAIL"

        print(f"\nOVERALL STATUS : {overall}\n")

        self.results.append({
            "metric": "OVERALL STATUS",
            "status": overall
        })

    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        pass
