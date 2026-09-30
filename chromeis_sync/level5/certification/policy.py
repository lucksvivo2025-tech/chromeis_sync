class CertificationPolicy:

    CERTIFIED_CLASSIFICATIONS = {
        "PROPER",
        "WHMCS_CREDIT_PRESENTATION_ONLY",
    }

    PENDING_EXCEPTION_CLASSIFICATIONS = {
        "TAX_PRESENTATION_ONLY",
    }

    BLOCKING_CLASSIFICATIONS = {
        "CREDIT_ALLOCATION",
        "COMMERCIAL_DIFFERENCE",
    }

    @classmethod
    def decide(cls, reconciliation_classification):

        classification = (
            reconciliation_classification
            or "UNKNOWN"
        )

        if classification in cls.CERTIFIED_CLASSIFICATIONS:
            return "CERTIFIED"

        if classification in cls.PENDING_EXCEPTION_CLASSIFICATIONS:
            return "PENDING_EXCEPTION"

        if classification in cls.BLOCKING_CLASSIFICATIONS:
            return "NOT_CERTIFIED"

        return "NOT_CERTIFIED"
