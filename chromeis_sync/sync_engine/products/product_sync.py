import frappe

from chromeis_sync.sync_engine.products.product_planner import ProductPlanner
from chromeis_sync.sync_engine.products.product_transaction import ProductTransaction


class ProductSync:

    def run(self):

        frappe.logger().info("Product Sync Started")

        product_ids = ProductPlanner.pending(1000)

        success = 0
        failed = 0

        for product_id in product_ids:

            try:
                ProductTransaction(product_id).execute()
                success += 1

            except Exception as e:

                failed += 1

                frappe.logger().error(
                    f"Product {product_id}: {str(e)}"
                )

        frappe.logger().info(f"Products Imported : {success}")
        frappe.logger().info(f"Products Failed   : {failed}")
        frappe.logger().info("Product Sync Finished")
