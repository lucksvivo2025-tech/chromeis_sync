from pprint import pformat

from chromeis_sync.sync_engine.framework.identity_recovery.partial_analyzer import (
    PartialInvoiceAnalyzer,
)
from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)


class TransformationAudit:

    @staticmethod
    def analyze(invoice_id):

        transformation = TransformationDetector.analyze(
            invoice_id
        )

        status = transformation["status"]

        report = {
            "invoice": invoice_id,
            "erp_invoice": transformation["erp_invoice"],
            "status": status,
            "summary": transformation,
            "explanation": "",
        }

        if status == "IDENTICAL":

            report["explanation"] = (
                "WHMCS invoice and ERP invoice have the same logical structure."
            )

        elif status == "COLLAPSED":

            report["explanation"] = (
                "Unsupported WHMCS items were absorbed into supported ERP rows while invoice totals remained identical."
            )

            report["details"] = PartialInvoiceAnalyzer.analyze(
                invoice_id
            )

        elif status == "MERGED":

            report["explanation"] = (
                "Multiple supported WHMCS items were merged into fewer ERP rows."
            )

            report["details"] = PartialInvoiceAnalyzer.analyze(
                invoice_id
            )

        elif status == "SPLIT":

            report["explanation"] = (
                "ERP contains more rows than the supported WHMCS structure."
            )

            report["details"] = PartialInvoiceAnalyzer.analyze(
                invoice_id
            )

        elif status == "PARTIAL":

            report["explanation"] = (
                "One or more WHMCS items could not be matched."
            )

            report["details"] = PartialInvoiceAnalyzer.analyze(
                invoice_id
            )

        elif status == "EMPTY":

            report["explanation"] = (
                "WHMCS invoice contains no invoice items."
            )

        else:

            report["explanation"] = (
                "Unknown transformation state."
            )

        return report

    @staticmethod
    def pretty(invoice_id):

        return pformat(
            TransformationAudit.analyze(
                invoice_id
            ),
            sort_dicts=False,
            width=120,
        )
