from chromeis_sync.migration_audit.repair_manifest import RepairManifest
from chromeis_sync.migration_audit.transaction import InvoiceTransaction


class RepairEngine:
    """
    Phase 7B Execution Engine

    Responsibilities:
    - Load repair manifest
    - Identify invoices requiring repair
    - Execute transactional repairs
    - Collect execution results

    NOTE:
    Version 1 intentionally repairs ONE invoice at a time.
    Batch execution will be added after production validation.
    """

    def __init__(self):
        self.manifest = RepairManifest().build()

    def repair_candidates(self):
        """
        Return only invoices that require repair.
        """
        return [
            row
            for row in self.manifest
            if row["repair_required"]
        ]

    def execute_one(self):
        """
        Execute the first pending repair.
        """

        candidates = self.repair_candidates()

        if not candidates:
            print("No invoices require repair.")
            return None

        candidate = candidates[0]

        print("=" * 60)
        print("Phase 7B Repair Engine")
        print("=" * 60)
        print(f"Invoice : {candidate['invoice_name']}")
        print(f"WHMCS ID: {candidate['whmcs_invoice_id']}")
        print(f"Reason  : {candidate['reason']}")
        print(f"Currency: {candidate['currency']}")
        print("=" * 60)

        result = InvoiceTransaction(
            candidate["invoice_name"],
            candidate["currency"]
        ).execute()

        return result

    def summary(self):
        """
        Display repair statistics.
        """

        total = len(self.manifest)
        repair = len(self.repair_candidates())
        ok = sum(1 for r in self.manifest if r["status"] == "OK")
        skip = sum(1 for r in self.manifest if r["status"] == "SKIP")

        print("=" * 60)
        print("Repair Manifest Summary")
        print("=" * 60)
        print(f"Total Invoices : {total}")
        print(f"OK             : {ok}")
        print(f"SKIP           : {skip}")
        print(f"REPAIR         : {repair}")
        print("=" * 60)
