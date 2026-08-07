import frappe

from chromeis_sync.sync_engine.products.group_planner import GroupPlanner
from chromeis_sync.sync_engine.products.group_transaction import GroupTransaction


class GroupSync:

    def run(self):

        frappe.logger().info("Item Group Sync Started")

        group_ids = GroupPlanner.pending(1000)

        success = 0
        failed = 0

        for group_id in group_ids:

            try:
                GroupTransaction(group_id).execute()
                success += 1

            except Exception as e:

                failed += 1

                frappe.logger().error(
                    f"Item Group {group_id}: {str(e)}"
                )

        frappe.logger().info(f"Item Groups Imported : {success}")
        frappe.logger().info(f"Item Groups Failed   : {failed}")
        frappe.logger().info("Item Group Sync Finished")
