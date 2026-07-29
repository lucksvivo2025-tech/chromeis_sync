from chromeis_sync.migration_audit.infrastructure.whmcs import WHMCSDatabase


class CustomerCreditValidator:
    """
    Validates current customer credit balances between
    WHMCS (Source of Truth) and ERPNext.
    """

    def __init__(self, verbose=True):
        self.verbose = verbose

    def run(self):
        print("=" * 80)
        print("CUSTOMER CREDIT VALIDATION")
        print("=" * 80)

        self.whmcs_summary()

        print("=" * 80)

    def whmcs_summary(self):
        print("\n--- WHMCS Customer Credit Summary -----------------------------")

        rows = WHMCSDatabase.query("""
            SELECT
                COUNT(*) AS customers,
                COALESCE(SUM(credit), 0) AS total_credit
            FROM tblclients
            WHERE credit > 0
        """)

        summary = rows[0]

        print(f"Customers with credit : {summary['customers']}")
        print(f"Total credit          : {float(summary['total_credit']):.2f}")
