class IdenticalRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "IdenticalRepair",
            "success": True,
            "updated": 0,
            "reason": "Already identical",
        }


class SplitRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "SplitRepair",
            "success": False,
            "updated": 0,
            "reason": "Split repair not implemented",
        }


class MergedRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "MergedRepair",
            "success": False,
            "updated": 0,
            "reason": "Merged repair not implemented",
        }


class CollapsedRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "CollapsedRepair",
            "success": False,
            "updated": 0,
            "reason": "Collapsed repair not implemented",
        }


class PartialRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "PartialRepair",
            "success": False,
            "updated": 0,
            "reason": "Partial repair not implemented",
        }


class LegacyFreeformRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "LegacyFreeformRepair",
            "success": False,
            "updated": 0,
            "reason": "Legacy freeform invoices cannot be repaired automatically",
        }


class EmptyRepair:

    @staticmethod
    def execute(invoice_id, analysis, commit=False):
        return {
            "strategy": "EmptyRepair",
            "success": False,
            "updated": 0,
            "reason": "No WHMCS invoice items found",
        }
