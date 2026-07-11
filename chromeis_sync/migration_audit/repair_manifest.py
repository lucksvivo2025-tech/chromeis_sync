import frappe

from collections import Counter

from chromeis_sync.migration_audit.repair_candidate_analyzer import (
    RepairCandidateAnalyzer,
)


class RepairManifest:

    def build(self):

        analyzer = RepairCandidateAnalyzer()

        results = analyzer.analyze_all()

        manifest = []

        for candidate in results:

            manifest.append({
                "invoice_name": candidate.invoice_name,
                "whmcs_invoice_id": candidate.whmcs_invoice_id,
                "status": candidate.status,
                "reason": ", ".join(candidate.reasons),
                "currency": candidate.currency,
                "conversion_rate": candidate.conversion_rate,
                "repair_required": candidate.repair_required,
            })

        return manifest

    def summary(self):

        manifest = self.build()

        counter = Counter(
            row["status"]
            for row in manifest
        )

        print("=" * 60)
        print("Repair Manifest Summary")
        print("=" * 60)

        print(f"Total Invoices : {len(manifest)}")
        print(f"OK             : {counter.get('OK', 0)}")
        print(f"INFO           : {counter.get('INFO', 0)}")
        print(f"SKIP           : {counter.get('SKIP', 0)}")
        print(f"REPAIR         : {counter.get('REPAIR', 0)}")

        print("=" * 60)

        return manifest
