"""
Simple Report Engine
"""


class ReportEngine:

    def __init__(self):
        self.reports = []

    def register(self, report):
        self.reports.append(report)

    def run(self):

        print("=" * 70)
        print("Chromeis Financial Reconciliation Engine")
        print("=" * 70)

        for report in self.reports:

            print()

            print(f"Running : {report.report_name}")

            report.start()
            report.execute()
            report.finish()

            print("Completed")
