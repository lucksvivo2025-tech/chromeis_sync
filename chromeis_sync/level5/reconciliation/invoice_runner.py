import frappe

from chromeis_sync.level5.classification.candidate_classifier import (
    CandidateClassifier,
)
from chromeis_sync.level5.classification.erp_candidate_collector import (
    ERPCandidateCollector,
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

            whmcs_invoice_id = str(whmcs_invoice_id)

            try:
                # -------------------------------------------------
                # 1. Discover every ERP candidate
                # -------------------------------------------------

                candidates = (
                    ERPCandidateCollector.sales_invoice(
                        whmcs_invoice_id
                    )
                )

                classification = CandidateClassifier.classify(
                    candidates,
                    authoritative_id=whmcs_invoice_id,
                )

                # -------------------------------------------------
                # 2. Missing / duplicate / unresolved cases
                #    cannot safely undergo normal invoice
                #    verification.
                # -------------------------------------------------

                if classification["classification"] in (
                    CandidateClassifier.MISSING,
                    CandidateClassifier.DUPLICATE,
                    CandidateClassifier.ORPHAN,
                    CandidateClassifier.UNRESOLVED,
                ):

                    result = {
                        "whmcs_id": whmcs_invoice_id,
                        "erp_id": classification.get("selected"),
                        "status": "NOT_VERIFIED",
                        "differences": [
                            {
                                "field": "classification",
                                "classification": classification[
                                    "classification"
                                ],
                                "reason": classification["reason"],
                                "candidates": classification[
                                    "candidates"
                                ],
                            }
                        ],
                    }

                    registry = InvoiceRegistryWriter.write(
                        result,
                        classification=classification[
                            "classification"
                        ],
                    )

                    result["registry"] = registry
                    results.append(result)

                    continue

                # -------------------------------------------------
                # 3. Safe candidate selected
                # -------------------------------------------------

                erp_id = classification["selected"]

                evidence = InvoiceCollector.collect(
                    whmcs_invoice_id,
                    erp_id,
                )

                # -------------------------------------------------
                # 4. Full verification
                # -------------------------------------------------

                result = InvoiceVerifier.verify(
                    evidence
                )

                # -------------------------------------------------
                # 5. Apply reconciliation classification
                # -------------------------------------------------

                from chromeis_sync.level5.classification.invoice_result_classifier import (
                    InvoiceResultClassifier,
                )

                result_classification = (
                    InvoiceResultClassifier.classify(
                        result,
                        evidence,
                    )
                )

                result["classification"] = result_classification

                result["candidate_classification"] = (
                    classification["classification"]
                )

                result["classification_reason"] = (
                    classification["reason"]
                )

                # -------------------------------------------------
                # 6. Persist Level 5 certification
                # -------------------------------------------------

                registry = InvoiceRegistryWriter.write(
                    result,
                    classification=result_classification,
                )

                result["registry"] = registry

                results.append(result)

            except Exception as exc:

                results.append({
                    "whmcs_id": whmcs_invoice_id,
                    "erp_id": None,
                    "status": "FAILED",
                    "differences": [
                        {
                            "field": "runner",
                            "error": type(exc).__name__,
                            "message": str(exc),
                        }
                    ],
                })

        frappe.db.commit()

        return results
