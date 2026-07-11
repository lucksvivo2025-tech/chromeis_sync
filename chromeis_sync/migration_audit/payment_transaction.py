import traceback

import frappe

from chromeis_sync.migration_audit.payment_snapshot import PaymentSnapshot
from chromeis_sync.migration_audit.payment_builder import PaymentBuilder


class PaymentTransaction:

    def __init__(self, payment_id):

        self.payment_id = int(payment_id)

    def execute(self):

        savepoint = f"payment_{self.payment_id}"

        print()
        print("=" * 60)
        print(f"WHMCS Payment : {self.payment_id}")
        print("=" * 60)

        frappe.db.savepoint(savepoint)

        try:

            # --------------------------------------------------
            # Duplicate Protection
            # --------------------------------------------------

            existing = frappe.db.get_value(
                "Payment Entry",
                {
                    "custom_whmcs_txn_id": str(self.payment_id),
                    "docstatus": ["!=", 2],
                },
                "name",
            )

            if existing:

                print(f"✓ Payment already migrated: {existing}")

                return {
                    "success": True,
                    "payment_entry": existing,
                    "duplicate": True,
                }

            # --------------------------------------------------
            # Snapshot
            # --------------------------------------------------

            snapshot = PaymentSnapshot.create(self.payment_id)

            # --------------------------------------------------
            # Build Payment Entry
            # --------------------------------------------------

            builder = PaymentBuilder(snapshot)

            payment_entry = builder.build()

            payment_entry.setup_party_account_field()
            payment_entry.set_missing_values()
            payment_entry.set_exchange_rate()
            payment_entry.set_amounts()

            # --------------------------------------------------
            # Insert & Submit
            # --------------------------------------------------

            payment_entry.insert()

            payment_entry.submit()

            # --------------------------------------------------
            # Verify GL
            # --------------------------------------------------

            gl_count = frappe.db.count(
                "GL Entry",
                {
                    "voucher_no": payment_entry.name
                }
            )

            if gl_count == 0:
                raise Exception(
                    "Payment Entry submitted but no GL Entries were created."
                )

            frappe.db.commit()

            print("✓ Payment Created")
            print(f"✓ Payment Entry : {payment_entry.name}")
            print(f"✓ GL Entries    : {gl_count}")
            print("✓ Transaction Committed")

            return {
                "success": True,
                "payment_entry": payment_entry.name,
                "gl_entries": gl_count,
            }

        except Exception:

            frappe.db.rollback(save_point=savepoint)

            print("✗ Transaction Rolled Back")

            traceback.print_exc()

            raise
