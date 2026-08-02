from chromeis_sync.migration_audit.financial_parity.invoice_parity import InvoiceParity
from chromeis_sync.migration_audit.financial_parity.payment_parity import PaymentParity
from chromeis_sync.migration_audit.financial_parity.payment_reference_parity import PaymentReferenceParity
from chromeis_sync.migration_audit.financial_parity.payment_ledger_parity import PaymentLedgerParity
from chromeis_sync.migration_audit.financial_parity.gl_parity import GLParity


class FinancialParityReport:

    def execute(self):

        print()
        print("=" * 80)
        print("CHROMEIS FINANCIAL PARITY REPORT")
        print("=" * 80)

        InvoiceParity().execute()

        print()

        PaymentParity().execute()

        print()

        PaymentReferenceParity().execute()

        print()

        PaymentLedgerParity().execute()

        print()

        GLParity().execute()

        print()
        print("=" * 80)
        print("FINANCIAL PARITY COMPLETE")
        print("=" * 80)
