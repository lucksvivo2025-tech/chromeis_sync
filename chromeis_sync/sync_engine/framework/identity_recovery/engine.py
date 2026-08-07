from chromeis_sync.sync_engine.framework.identity_recovery.entities.invoice_item import (
    InvoiceItemRecoveryAnalyzer,
)
from chromeis_sync.sync_engine.framework.identity_recovery.validator import (
    IdentityRecoveryValidator,
)
from chromeis_sync.sync_engine.framework.identity_recovery.recover import (
    IdentityRecovery,
)


class IdentityRecoveryEngine:

    @staticmethod
    def invoice(invoice_id, commit=False):

        analysis = InvoiceItemRecoveryAnalyzer.analyze(invoice_id)

        validation = IdentityRecoveryValidator.invoice(invoice_id)

        recovery = None

        if commit and validation["valid"]:
            recovery = IdentityRecovery.invoice(
                invoice_id,
                commit=True,
            )

        return {
            "invoice": invoice_id,
            "analysis": analysis,
            "validation": validation,
            "recovery": recovery,
        }

    @staticmethod
    def analyze(invoice_id):

        return InvoiceItemRecoveryAnalyzer.analyze(invoice_id)

    @staticmethod
    def validate(invoice_id):

        return IdentityRecoveryValidator.invoice(invoice_id)

    @staticmethod
    def recover(invoice_id, commit=False):

        return IdentityRecovery.invoice(
            invoice_id,
            commit=commit,
        )
