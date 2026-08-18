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
                candidates = (
                    ERPCandidateCollector.sales_invoice(
                        whmcs_invoice_id
                    )
                )

                identity_result = CandidateClassifier.classify(
                    candidates,
                    authoritative_id=whmcs_invoice_id,
                )

                if identity_result["classification"] in (
                    CandidateClassifier.MISSING,
                    CandidateClassifier.DUPLICATE,
                    CandidateClassifier.ORPHAN,
                    CandidateClassifier.UNRESOLVED,
                ):

                    result = {
                        "whmcs_id": whmcs_invoice_id,
                        "erp_id": identity_result.get("selected"),
                        "status": "NOT_VERIFIED",
                        "differences": [
                            {
                                "field": "classification",
                                "classification": identity_result[
                                    "classification"
                                ],
                                "reason": identity_result["reason"],
                                "candidates": identity_result[
                                    "candidates"
                                ],
                            }
                        ],
                        "identity_classification": identity_result[
                            "classification"
                        ],
                    }

                    registry = InvoiceRegistryWriter.write(
                        result,
                        identity_classification=identity_result[
                            "classification"
                        ],
                    )

                    result["registry"] = registry
                    results.append(result)

                    continue

                erp_id = identity_result["selected"]

                evidence = InvoiceCollector.collect(
                    whmcs_invoice_id,
                    erp_id,
                )

                result = InvoiceVerifier.verify(
                    evidence
                )

                from chromeis_sync.level5.classification.invoice_result_classifier import (
                    InvoiceResultClassifier,
                )

                reconciliation_result = (
                    InvoiceResultClassifier.classify(
                        result,
                        evidence,
                    )
                )

                result["reconciliation_classification"] = (
                    reconciliation_result
                )

                if reconciliation_result in (
                    "TAX_PRESENTATION_ONLY",
                    "WHMCS_CREDIT_PRESENTATION_ONLY",
                    "CURRENCY_PRESENTATION_ONLY",
                ):
                    result["status"] = "VERIFIED"


                result["reconciliation_classification"] = (
                    reconciliation_result
                )

                result["identity_classification"] = (
                    identity_result["classification"]
                )

                result["classification_reason"] = (
                    identity_result["reason"]
                )

                registry = InvoiceRegistryWriter.write(
                    result,
                    identity_classification=identity_result[
                        "classification"
                    ],
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
