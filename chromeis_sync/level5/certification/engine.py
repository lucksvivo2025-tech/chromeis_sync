from chromeis_sync.level5.certification.models import CertificationResult
from chromeis_sync.level5.certification.policy import CertificationPolicy


class CertificationEngine:
    """
    Final Level 5 certification authority.

    This class does not collect evidence, perform repairs,
    or query WHMCS/ERP.

    It converts validated Level 5 findings into a deterministic
    accounting certification decision.
    """

    @classmethod
    def certify(
        cls,
        entity_type,
        erp_id,
        whmcs_id,
        identity_classification,
        verification_result,
        reconciliation_classification,
        evidence_complete,
        differences=None,
        warnings=None,
        evidence_snapshot=None,
    ):

        differences = differences or []
        warnings = warnings or []
        evidence_snapshot = evidence_snapshot or {}

        result = CertificationResult(
            entity_type=entity_type,
            erp_id=str(erp_id or ""),
            whmcs_id=str(whmcs_id or ""),
            identity_classification=identity_classification or "",
            verification_result=(
                verification_result or "NOT_VERIFIED"
            ),
            reconciliation_classification=(
                reconciliation_classification or ""
            ),
            evidence_complete=bool(evidence_complete),
            differences=differences,
            warnings=warnings,
            evidence_snapshot=evidence_snapshot,
        )

        # ---------------------------------------------------------
        # 1. Evidence completeness
        # ---------------------------------------------------------

        if not evidence_complete:
            result.certification_status = "NOT_CERTIFIED"
            result.reasons.append(
                "Required evidence is incomplete."
            )
            return result

        # ---------------------------------------------------------
        # 2. Identity
        #
        # Normal invoices require PROPER identity.
        #
        # CANCELLED_REVERSED invoices may also be certified when
        # their complete Level 5 evidence is verified and their
        # reconciliation classification is PROPER.
        #
        # This does NOT certify cancelled/reversed invoices with
        # commercial, credit, or other unresolved differences.
        # ---------------------------------------------------------

        identity_is_certifiable = (
            identity_classification == "PROPER"
            or (
                identity_classification
                == "CANCELLED_REVERSED"
                and reconciliation_classification
                == "PROPER"
            )
        )

        if not identity_is_certifiable:
            result.certification_status = "NOT_CERTIFIED"
            result.reasons.append(
                "Identity is not certifiable: "
                f"{identity_classification or 'UNKNOWN'}"
            )
            return result

        # ---------------------------------------------------------
        # 3. Verification
        #
        # Certification requires VERIFIED.
        # No exception is silently accepted here.
        # ---------------------------------------------------------

        if verification_result != "VERIFIED":
            result.certification_status = "NOT_CERTIFIED"
            result.reasons.append(
                f"Verification result is not VERIFIED: "
                f"{verification_result or 'NOT_VERIFIED'}"
            )
            return result

        # ---------------------------------------------------------
        # 4. Reconciliation policy
        # ---------------------------------------------------------

        decision = CertificationPolicy.decide(
            reconciliation_classification
        )

        if decision == "PENDING_EXCEPTION":
            result.certification_status = "PENDING_EXCEPTION"
            result.reasons.append(
                "Accounting difference is explicitly "
                "classified as a pending exception."
            )
            return result

        if decision == "NOT_CERTIFIED":
            result.certification_status = "NOT_CERTIFIED"
            result.reasons.append(
                "Reconciliation classification is not "
                "approved for certification: "
                f"{reconciliation_classification or 'UNKNOWN'}"
            )
            return result

        # ---------------------------------------------------------
        # 5. Verification authority
        #
        # InvoiceVerifier has already determined whether the
        # differences are blocking or non-blocking. Do not reject
        # certification merely because forensic differences are
        # preserved in the evidence.
        #
        # VERIFIED means no blocking difference remains.
        # ---------------------------------------------------------

        if verification_result != "VERIFIED":
            result.certification_status = "NOT_CERTIFIED"
            result.reasons.append(
                "Validation produced a non-verified result."
            )
            return result

        # ---------------------------------------------------------
        # 6. Final certification
        # ---------------------------------------------------------

        result.certification_status = "CERTIFIED"
        result.reasons.append(
            "All required evidence and mandatory validations passed."
        )

        return result
