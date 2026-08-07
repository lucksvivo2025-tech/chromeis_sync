from chromeis_sync.sync_engine.framework.identity_recovery.validator import (
    IdentityRecoveryValidator,
)
from chromeis_sync.sync_engine.framework.identity_recovery.transformation_detector import (
    TransformationDetector,
)


class MigrationQualityEngine:

    @staticmethod
    def invoice(invoice_id):

        identity = IdentityRecoveryValidator.invoice(
            invoice_id
        )

        transformation = (
            TransformationDetector.analyze(
                invoice_id
            )
        )

        score = 100

        deductions = []

        #
        # Identity Recovery
        #

        if not identity["valid"]:

            score -= 40

            deductions.append(
                "Identity recovery incomplete"
            )

        #
        # Transformation
        #

        status = transformation["status"]

        if status == "IDENTICAL":
            pass

        elif status == "COLLAPSED":

            score -= 5

            deductions.append(
                "Unsupported items collapsed"
            )

        elif status == "MERGED":

            score -= 10

            deductions.append(
                "Multiple WHMCS rows merged"
            )

        elif status == "SPLIT":

            score -= 10

            deductions.append(
                "ERP rows split"
            )

        elif status == "PARTIAL":

            score -= 30

            deductions.append(
                "Transformation partial"
            )

        elif status == "EMPTY":

            score -= 50

            deductions.append(
                "No WHMCS items"
            )

        else:

            score -= 50

            deductions.append(
                status
            )

        score = max(
            score,
            0,
        )

        if score >= 95:
            grade = "A"

        elif score >= 85:
            grade = "B"

        elif score >= 70:
            grade = "C"

        elif score >= 50:
            grade = "D"

        else:
            grade = "F"

        return {

            "invoice": invoice_id,

            "erp_invoice": identity.get(
                "erp_invoice"
            ),

            "identity": identity,

            "transformation": transformation,

            "score": score,

            "grade": grade,

            "deductions": deductions,
        }
