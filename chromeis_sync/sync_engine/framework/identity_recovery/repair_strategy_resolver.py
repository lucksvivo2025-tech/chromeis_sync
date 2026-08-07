class RepairStrategyResolver:

    DRAFT_MUTATION = "DRAFT_MUTATION"

    SUBMITTED_AMEND = "SUBMITTED_AMEND"

    CANCELLED_RECREATE = "CANCELLED_RECREATE"

    @classmethod
    def resolve(cls, invoice):

        if invoice.docstatus == 0:

            return cls.DRAFT_MUTATION

        if invoice.docstatus == 1:

            return cls.SUBMITTED_AMEND

        if invoice.docstatus == 2:

            return cls.CANCELLED_RECREATE

        raise Exception(
            f"Unknown docstatus {invoice.docstatus}"
        )
