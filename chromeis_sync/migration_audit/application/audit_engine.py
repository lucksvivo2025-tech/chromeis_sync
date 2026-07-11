from __future__ import annotations

from typing import Iterable

from chromeis_sync.migration_audit.domain.audit.audit_result import AuditResult
from chromeis_sync.migration_audit.domain.matchers.identity_matcher import IdentityMatcher
from chromeis_sync.migration_audit.domain.normalizers.identity_extractor import (
    IdentityExtractor,
)
from chromeis_sync.migration_audit.infrastructure.providers.snapshot_provider import (
    SnapshotProvider,
)
from chromeis_sync.migration_audit.infrastructure.providers.whmcs_provider import (
    WHMCSProvider,
)


class AuditEngine:
    """
    Coordinates the migration audit.

    No SQL.
    No parsing logic.
    No matching logic.

    It orchestrates the existing components.
    """

    def __init__(self):

        self.whmcs_provider = WHMCSProvider()
        self.snapshot_provider = SnapshotProvider()

        self.extractor = IdentityExtractor()
        self.matcher = IdentityMatcher()

    def audit(
        self,
        whmcs_invoice_id: int,
        erp_invoice_name: str,
    ) -> AuditResult:

        whmcs_invoice = self.whmcs_provider.load_invoice(
            whmcs_invoice_id
        )

        snapshot = self.snapshot_provider.load(
            erp_invoice_name
        )

        if not whmcs_invoice.items:
            raise ValueError(
                "WHMCS invoice has no items."
            )

        if not snapshot.items:
            raise ValueError(
                "ERP invoice has no items."
            )

        whmcs_identity = self.extractor.extract(
            whmcs_invoice.items[0].description
        )

        erp_identity = self.extractor.extract(
            snapshot.items[0].description
        )

        identity_result = self.matcher.match(
            whmcs_identity,
            erp_identity,
        )

        return AuditResult(
            whmcs_invoice_id=whmcs_invoice_id,
            erp_invoice_name=erp_invoice_name,
            identity_result=identity_result,
        )

    def audit_many(
        self,
        audits: list[tuple[int, str]],
    ) -> list[AuditResult]:
        """
        Audit multiple WHMCS/ERP invoice pairs.
        """

        results = []

        for whmcs_invoice_id, erp_invoice_name in audits:

            try:

                result = self.audit(
                    whmcs_invoice_id=whmcs_invoice_id,
                    erp_invoice_name=erp_invoice_name,
                )

                results.append(result)

            except Exception as e:

                print(
                    f"[FAILED] WHMCS {whmcs_invoice_id} -> {erp_invoice_name}"
                )

                print(f"Type   : {type(e).__name__}")
                print(f"Reason : {e}")
                print("-" * 60)

        return results

    def audit_all(
        self,
    ) -> list[AuditResult]:
        """
        Audit every migrated invoice.
        """

        audits = self.snapshot_provider.list_migrated_invoices()

        print(f"Found {len(audits)} migrated invoices.")
        print("Starting audit...\n")

        results = self.audit_many(audits)

        passed = sum(
            1
            for r in results
            if r.identity_result.matched
        )

        failed = len(results) - passed

        print("\n==============================")
        print("Migration Audit Summary")
        print("==============================")
        print(f"Total Audited : {len(results)}")
        print(f"Passed        : {passed}")
        print(f"Failed        : {failed}")

        return results
