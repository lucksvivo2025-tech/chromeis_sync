from chromeis_sync.sync_engine.audit.parity_report import ParityReport


class FinancialReconcile:

    def run(self):

        print()
        print("=" * 70)
        print("           WHMCS → ERP FINANCIAL PARITY REPORT")
        print("=" * 70)
        print()

        results = ParityReport.run()

        passed = 0
        failed = 0

        for row in results:

            print(f"Module      : {row['module']}")
            print(f"WHMCS Count : {row['whmcs']}")
            print(f"ERP Count   : {row['erp']}")
            print(f"Difference  : {row['difference']}")
            print(f"Status      : {row['status']}")
            print("-" * 70)

            if row["status"] == "PASS":
                passed += 1
            else:
                failed += 1

        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Passed : {passed}")
        print(f"Failed : {failed}")

        if failed == 0:
            print()
            print("✔ WHMCS and ERP are financially synchronized.")
        else:
            print()
            print("✘ Financial parity differences detected.")

        print("=" * 70)

        return results
