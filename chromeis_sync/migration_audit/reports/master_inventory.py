import frappe

from chromeis_sync.migration_audit.reports.core.base_report import BaseReport


class MasterInventoryReport(BaseReport):

    report_id = "R001"
    report_name = "Master Inventory"

    def execute(self):

        self.compare(
            "Customers",
            "SELECT COUNT(*) FROM whmcs_mirror.tblclients",
            """
            SELECT COUNT(*)
            FROM `tabCustomer`
            WHERE custom_whmcs_client_id REGEXP '^[0-9]+$'
            """
        )


def execute():

    report = MasterInventoryReport()

    report.start()

    report.execute()

    report.finish()

    return report.results
