class EvidenceValidator:
    """
    Determines whether Level 5 has sufficient evidence to
    make an accounting certification decision.

    This class does not decide whether accounting is correct.
    It only determines whether the required evidence exists.
    """

    REQUIRED_KEYS = (
        "whmcs_id",
        "erp_id",
        "source_mode",
        "relationship_source",
        "mirror_applicable",
        "api",
        "mirror",
        "whmcs_transactions",
        "whmcs_credits",
        "erp_payments",
        "erp_transaction_payments",
        "erp_journals",
        "erp",
    )

    @classmethod
    def validate(cls, evidence):

        errors = []
        warnings = []

        if not isinstance(evidence, dict):
            return False, [
                "Evidence object is missing or is not a dictionary."
            ], warnings

        # ---------------------------------------------------------
        # Required evidence containers
        # ---------------------------------------------------------

        for key in cls.REQUIRED_KEYS:

            if key not in evidence:
                errors.append(
                    f"Required evidence key missing: {key}"
                )

        if errors:
            return False, errors, warnings

        # ---------------------------------------------------------
        # Identity
        # ---------------------------------------------------------

        if not evidence.get("whmcs_id"):
            errors.append(
                "WHMCS invoice identity is missing."
            )

        if not evidence.get("erp_id"):
            errors.append(
                "ERP invoice identity is missing."
            )

        # ---------------------------------------------------------
        # WHMCS API
        # ---------------------------------------------------------

        api = evidence.get("api")

        if not isinstance(api, dict) or not api:
            errors.append(
                "WHMCS API invoice evidence is missing."
            )

        # ---------------------------------------------------------
        # Source provenance / WHMCS Mirror
        # ---------------------------------------------------------

        source_mode = evidence.get(
            "source_mode"
        )

        relationship_source = evidence.get(
            "relationship_source"
        )

        mirror_applicable = evidence.get(
            "mirror_applicable"
        )

        if source_mode == "HISTORICAL_SNAPSHOT":

            if mirror_applicable is not True:
                errors.append(
                    "Historical source mode requires "
                    "mirror_applicable=True."
                )

            if relationship_source != "WHMCS_MIRROR":
                errors.append(
                    "Historical source mode requires "
                    "WHMCS_MIRROR relationship evidence."
                )

            if evidence.get("mirror") is None:
                errors.append(
                    "WHMCS mirror invoice record is missing."
                )

        elif source_mode == "LIVE_POST_SNAPSHOT":

            if mirror_applicable is not False:
                errors.append(
                    "Post-snapshot source mode requires "
                    "mirror_applicable=False."
                )

            if relationship_source != "WHMCS_LIVE_API":
                errors.append(
                    "Post-snapshot source mode requires "
                    "WHMCS_LIVE_API relationship evidence."
                )

        else:
            errors.append(
                "Source evidence mode is missing or invalid."
            )

        # ---------------------------------------------------------
        # ERP invoice
        # ---------------------------------------------------------

        erp = evidence.get("erp")

        if not isinstance(erp, dict) or not erp:
            errors.append(
                "ERP Sales Invoice evidence is missing."
            )

        # ---------------------------------------------------------
        # Relationship evidence
        #
        # Empty collections are valid. They mean no corresponding
        # records were found.
        #
        # What is invalid is the collection itself being absent,
        # which is already checked above.
        # ---------------------------------------------------------

        collection_keys = (
            "whmcs_transactions",
            "whmcs_credits",
            "erp_payments",
            "erp_transaction_payments",
            "erp_journals",
        )

        for key in collection_keys:

            value = evidence.get(key)

            if not isinstance(value, list):
                errors.append(
                    f"Evidence collection '{key}' "
                    f"must be a list."
                )

        # ---------------------------------------------------------
        # Explain legitimate empty relationship sets
        # ---------------------------------------------------------

        if (
            isinstance(
                evidence.get("whmcs_transactions"),
                list,
            )
            and not evidence["whmcs_transactions"]
        ):
            warnings.append(
                "No WHMCS payment transactions found "
                "for this invoice."
            )

        if (
            isinstance(
                evidence.get("whmcs_credits"),
                list,
            )
            and not evidence["whmcs_credits"]
        ):
            warnings.append(
                "No WHMCS credit records found "
                "for this invoice."
            )

        if (
            isinstance(
                evidence.get("erp_payments"),
                list,
            )
            and not evidence["erp_payments"]
        ):
            warnings.append(
                "No ERP Payment Entry allocations found "
                "for this invoice."
            )

        if (
            isinstance(
                evidence.get("erp_journals"),
                list,
            )
            and not evidence["erp_journals"]
        ):
            warnings.append(
                "No ERP credit Journal Entries found "
                "for this invoice."
            )

        return (
            len(errors) == 0,
            errors,
            warnings,
        )
