class SourceEvidencePolicy:
    """
    Defines which WHMCS source-evidence regime applies to an invoice.

    WHMCS mirror is preserved as a historical snapshot. Evidence gathered
    after that snapshot boundary must come from the live WHMCS API and
    must not be represented as mirror evidence.
    """

    HISTORICAL_SNAPSHOT = "HISTORICAL_SNAPSHOT"
    LIVE_POST_SNAPSHOT = "LIVE_POST_SNAPSHOT"

    # Technical evidence boundary established from the preserved
    # whmcs_mirror / temp_whmcs_import snapshot.
    SNAPSHOT_MAX_INVOICE_ID = 9740

    @classmethod
    def source_mode(cls, whmcs_invoice_id):
        invoice_id = int(str(whmcs_invoice_id))

        if invoice_id <= cls.SNAPSHOT_MAX_INVOICE_ID:
            return cls.HISTORICAL_SNAPSHOT

        return cls.LIVE_POST_SNAPSHOT

    @classmethod
    def mirror_applicable(cls, whmcs_invoice_id):
        return (
            cls.source_mode(whmcs_invoice_id)
            == cls.HISTORICAL_SNAPSHOT
        )
