import frappe

from chromeis_sync.sync_engine.payments.payment_transaction import PaymentTransaction


class PaymentSync:

    def run(self):

        frappe.logger().info("Payment Sync Started")

        payment_ids = frappe.db.sql("""
            SELECT id
            FROM whmcs_mirror.tblaccounts
            ORDER BY id
        """, as_dict=True)

        success = 0
        failed = 0
        skipped = 0

        for row in payment_ids:

            try:

                result = PaymentTransaction(row["id"]).execute()

                if result is None:
                    skipped += 1
                else:
                    success += 1

            except Exception as e:

                failed += 1

                frappe.logger().error(
                    f"Payment {row['id']}: {str(e)}"
                )

        frappe.logger().info(f"Payments Imported : {success}")
        frappe.logger().info(f"Payments Skipped  : {skipped}")
        frappe.logger().info(f"Payments Failed   : {failed}")
        frappe.logger().info("Payment Sync Finished")
