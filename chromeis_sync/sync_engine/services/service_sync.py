import frappe

from chromeis_sync.sync_engine.services.service_planner import ServicePlanner
from chromeis_sync.sync_engine.services.service_transaction import ServiceTransaction


class ServiceSync:

    def run(self):

        frappe.logger().info("Service Sync Started")

        service_ids = ServicePlanner.pending(1000)

        success = 0
        failed = 0

        for service_id in service_ids:

            try:
                ServiceTransaction(service_id).execute()
                success += 1

            except Exception as e:

                failed += 1

                frappe.logger().error(
                    f"Service {service_id}: {str(e)}"
                )

        frappe.logger().info(
            f"Services Imported : {success}"
        )

        frappe.logger().info(
            f"Services Failed   : {failed}"
        )

        frappe.logger().info(
            "Service Sync Finished"
        )
