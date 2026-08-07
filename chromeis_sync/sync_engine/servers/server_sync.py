import frappe

from chromeis_sync.sync_engine.servers.server_planner import ServerPlanner
from chromeis_sync.sync_engine.servers.server_transaction import ServerTransaction


class ServerSync:

    def run(self):

        frappe.logger().info("Server Sync Started")

        server_ids = ServerPlanner.pending(1000)

        success = 0
        failed = 0

        for server_id in server_ids:

            try:
                ServerTransaction(server_id).execute()
                success += 1

            except Exception as e:

                failed += 1

                frappe.logger().error(
                    f"Server {server_id}: {str(e)}"
                )

        frappe.logger().info(f"Servers Imported : {success}")
        frappe.logger().info(f"Servers Failed   : {failed}")
        frappe.logger().info("Server Sync Finished")
