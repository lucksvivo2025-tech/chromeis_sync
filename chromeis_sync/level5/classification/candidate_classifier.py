from dataclasses import dataclass, field


@dataclass
class ERPCandidate:
    erp_id: str
    doctype: str
    docstatus: int | None = None
    status: str | None = None
    evidence: dict = field(default_factory=dict)


class CandidateClassifier:

    PROPER = "PROPER"
    HISTORICAL = "HISTORICAL"
    CANCELLED_REVERSED = "CANCELLED_REVERSED"
    DUPLICATE = "DUPLICATE"
    ORPHAN = "ORPHAN"
    MISSING = "MISSING"
    UNRESOLVED = "UNRESOLVED"

    @classmethod
    def classify(cls, candidates, authoritative_id=None):

        if not candidates:
            return {
                "classification": cls.MISSING,
                "selected": None,
                "candidates": [],
                "reason": "No ERP candidate found.",
            }

        if len(candidates) > 1:
            return {
                "classification": cls.DUPLICATE,
                "selected": None,
                "candidates": [
                    cls._serialize(candidate)
                    for candidate in candidates
                ],
                "reason": "Multiple ERP candidates require reconciliation.",
            }

        candidate = candidates[0]

        if not authoritative_id:
            return {
                "classification": cls.ORPHAN,
                "selected": None,
                "candidates": [cls._serialize(candidate)],
                "reason": "ERP candidate has no authoritative WHMCS identity.",
            }

        if candidate.docstatus == 2:
            classification = cls.CANCELLED_REVERSED

        elif candidate.evidence.get("historical"):
            classification = cls.HISTORICAL

        elif candidate.docstatus == 1:
            classification = cls.PROPER

        else:
            classification = cls.UNRESOLVED

        return {
            "classification": classification,
            "selected": candidate.erp_id
            if classification in (
                cls.PROPER,
                cls.HISTORICAL,
                cls.CANCELLED_REVERSED,
            )
            else None,
            "candidates": [cls._serialize(candidate)],
            "reason": cls._reason(classification),
        }

    @staticmethod
    def _serialize(candidate):
        return {
            "erp_id": candidate.erp_id,
            "doctype": candidate.doctype,
            "docstatus": candidate.docstatus,
            "status": candidate.status,
            "evidence": candidate.evidence,
        }

    @staticmethod
    def _reason(classification):
        reasons = {
            "PROPER": "Single submitted ERP candidate.",
            "HISTORICAL": "ERP candidate identified as historical/legacy.",
            "CANCELLED_REVERSED": "ERP candidate is cancelled/reversed.",
            "DUPLICATE": "Multiple ERP candidates found.",
            "ORPHAN": "ERP candidate has no WHMCS identity.",
            "MISSING": "No ERP candidate found.",
            "UNRESOLVED": "ERP candidate could not be safely classified.",
        }

        return reasons.get(
            classification,
            "Classification requires review.",
        )
