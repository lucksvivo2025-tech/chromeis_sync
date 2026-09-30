import frappe

from chromeis_sync.level5.certification.engine import (
    CertificationEngine,
)
from chromeis_sync.level5.certification.evidence_validator import (
    EvidenceValidator,
)
from chromeis_sync.level5.classification.candidate_classifier import (
    CandidateClassifier,
)
from chromeis_sync.level5.classification.erp_candidate_collector import (
    ERPCandidateCollector,
)
from chromeis_sync.level5.classification.invoice_result_classifier import (
    InvoiceResultClassifier,
)
from chromeis_sync.level5.collectors.invoice_collector import (
    InvoiceCollector,
)
from chromeis_sync.level5.reconciliation.invoice_registry import (
    InvoiceRegistryWriter,
)
from chromeis_sync.level5.validators.invoice_verifier import (
    InvoiceVerifier,
)


class InvoiceVerificationRunner:

    @classmethod
    def run(cls, whmcs_invoice_ids):

        results = []

        for whmcs_invoice_id in whmcs_invoice_ids:

            whmcs_invoice_id = str(
                whmcs_invoice_id
            )

            try:

                # -------------------------------------------------
                # 1. Identity
                # -------------------------------------------------

                candidates = (
                    ERPCandidateCollector.sales_invoice(
                        whmcs_invoice_id
                    )
                )

                identity_result = (
                    CandidateClassifier.classify(
                        candidates,
                        authoritative_id=whmcs_invoice_id,
                    )
                )

                identity_classification = (
                    identity_result["classification"]
                )

                # -------------------------------------------------
                # 2. Identity failure
                #
                # No ERP candidate can be certified.
                # -------------------------------------------------

                if identity_classification in (
                    CandidateClassifier.MISSING,
                    CandidateClassifier.DUPLICATE,
                    CandidateClassifier.ORPHAN,
                    CandidateClassifier.UNRESOLVED,
                ):

                    result = {
                        "whmcs_id": whmcs_invoice_id,
                        "erp_id": identity_result.get(
                            "selected"
                        ),
                        "status": "NOT_VERIFIED",
                        "verification_result": (
                            "NOT_VERIFIED"
                        ),
                        "identity_classification": (
                            identity_classification
                        ),
                        "reconciliation_classification": "",
                        "evidence_complete": False,
                        "evidence_errors": [
                            identity_result["reason"]
                        ],
                        "evidence_warnings": [],
                        "differences": [
                            {
                                "field": "classification",
                                "classification": (
                                    identity_classification
                                ),
                                "reason": (
                                    identity_result["reason"]
                                ),
                                "candidates": (
                                    identity_result[
                                        "candidates"
                                    ]
                                ),
                            }
                        ],
                        "certification_status": (
                            "NOT_CERTIFIED"
                        ),
                        "certification_reasons": [
                            "ERP invoice identity "
                            "could not be established."
                        ],
                    }

                    registry = (
                        InvoiceRegistryWriter.write(
                            result,
                            identity_classification=(
                                identity_classification
                            ),
                        )
                    )

                    result["registry"] = registry
                    results.append(result)

                    continue

                # -------------------------------------------------
                # 3. ERP identity established
                # -------------------------------------------------

                erp_id = identity_result["selected"]

                # -------------------------------------------------
                # 4. Collect complete evidence
                # -------------------------------------------------

                evidence = InvoiceCollector.collect(
                    whmcs_invoice_id,
                    erp_id,
                )

                # -------------------------------------------------
                # 5. Evidence completeness
                # -------------------------------------------------

                (
                    evidence_complete,
                    evidence_errors,
                    evidence_warnings,
                ) = EvidenceValidator.validate(
                    evidence
                )

                # -------------------------------------------------
                # Fail closed if evidence incomplete
                # -------------------------------------------------

                if not evidence_complete:

                    result = {
                        "whmcs_id": whmcs_invoice_id,
                        "erp_id": erp_id,
                        "status": "NOT_VERIFIED",
                        "verification_result": (
                            "NOT_VERIFIED"
                        ),
                        "identity_classification": (
                            identity_classification
                        ),
                        "reconciliation_classification": "",
                        "evidence_complete": False,
                        "evidence_errors": (
                            evidence_errors
                        ),
                        "evidence_warnings": (
                            evidence_warnings
                        ),
                        "differences": [
                            {
                                "field": (
                                    "evidence_completeness"
                                ),
                                "classification": (
                                    "EVIDENCE_INCOMPLETE"
                                ),
                                "errors": (
                                    evidence_errors
                                ),
                            }
                        ],
                        "certification_status": (
                            "NOT_CERTIFIED"
                        ),
                        "certification_reasons": (
                            [
                                "Required evidence "
                                "is incomplete."
                            ]
                        ),
                        "evidence_snapshot": evidence,
                    }

                    registry = (
                        InvoiceRegistryWriter.write(
                            result,
                            identity_classification=(
                                identity_classification
                            ),
                        )
                    )

                    result["registry"] = registry
                    results.append(result)

                    continue

                # -------------------------------------------------
                # 6. Accounting verification
                # -------------------------------------------------

                verification = InvoiceVerifier.verify(
                    evidence
                )

                verification_result = (
                    verification.get("status")
                    or "NOT_VERIFIED"
                )

                differences = (
                    verification.get("differences")
                    or []
                )

                # -------------------------------------------------
                # 7. Accounting classification
                # -------------------------------------------------

                reconciliation_classification = (
                    InvoiceResultClassifier.classify(
                        verification,
                        evidence,
                    )
                )

                # -------------------------------------------------
                # IMPORTANT:
                #
                # Never override verification status merely
                # because a classification is presentation-only.
                #
                # CertificationEngine is now the authority.
                # -------------------------------------------------

                # -------------------------------------------------
                # 8. Final certification
                # -------------------------------------------------

                certification = (
                    CertificationEngine.certify(
                        entity_type="Invoice",
                        erp_id=erp_id,
                        whmcs_id=whmcs_invoice_id,
                        identity_classification=(
                            identity_classification
                        ),
                        verification_result=(
                            verification_result
                        ),
                        reconciliation_classification=(
                            reconciliation_classification
                        ),
                        evidence_complete=True,
                        differences=differences,
                        warnings=evidence_warnings,
                        evidence_snapshot=evidence,
                    )
                )

                # -------------------------------------------------
                # 9. Build durable result
                # -------------------------------------------------

                result = dict(verification)

                result["whmcs_id"] = (
                    whmcs_invoice_id
                )

                result["erp_id"] = erp_id

                result["verification_result"] = (
                    verification_result
                )

                result["identity_classification"] = (
                    identity_classification
                )

                result["reconciliation_classification"] = (
                    reconciliation_classification
                )

                result["evidence_complete"] = True

                result["evidence_errors"] = (
                    evidence_errors
                )

                result["evidence_warnings"] = (
                    evidence_warnings
                )

                result["certification_status"] = (
                    certification.certification_status
                )

                result["certification_reasons"] = (
                    certification.reasons
                )

                result["evidence_snapshot"] = (
                    evidence
                )

                result["classification_reason"] = (
                    identity_result["reason"]
                )

                # -------------------------------------------------
                # 10. Registry persistence
                # -------------------------------------------------

                registry = (
                    InvoiceRegistryWriter.write(
                        result,
                        identity_classification=(
                            identity_classification
                        ),
                    )
                )

                result["registry"] = registry

                results.append(result)

            except Exception as exc:

                # -------------------------------------------------
                # System failure is NEVER treated as verification.
                # -------------------------------------------------

                results.append({
                    "whmcs_id": whmcs_invoice_id,
                    "erp_id": None,
                    "status": "FAILED",
                    "verification_result": "FAILED",
                    "certification_status": (
                        "NOT_CERTIFIED"
                    ),
                    "differences": [
                        {
                            "field": "runner",
                            "error": type(exc).__name__,
                            "message": str(exc),
                        }
                    ],
                    "certification_reasons": [
                        "Level 5 execution failed."
                    ],
                })

        frappe.db.commit()

        return results
