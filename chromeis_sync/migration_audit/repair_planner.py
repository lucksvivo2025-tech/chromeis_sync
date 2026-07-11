from collections import Counter

from chromeis_sync.migration_audit.repair_manifest import RepairManifest


class RepairPlanner:

    def __init__(self):

        self.manifest = RepairManifest().build()

    def plan(self):

        """
        Return only invoices that actually require repair.
        """

        return [
            row
            for row in self.manifest
            if row["repair_required"]
        ]

    def statistics(self):

        counter = Counter(
            row["status"]
            for row in self.manifest
        )

        return {
            "total": len(self.manifest),
            "ok": counter.get("OK", 0),
            "info": counter.get("INFO", 0),
            "skip": counter.get("SKIP", 0),
            "repair": counter.get("REPAIR", 0),
        }

    def print_summary(self):

        stats = self.statistics()

        print("=" * 60)
        print("Repair Planner Summary")
        print("=" * 60)
        print(f"Total   : {stats['total']}")
        print(f"OK      : {stats['ok']}")
        print(f"INFO    : {stats['info']}")
        print(f"SKIP    : {stats['skip']}")
        print(f"REPAIR  : {stats['repair']}")
        print("=" * 60)

    def has_repairs(self):

        return len(self.plan()) > 0
