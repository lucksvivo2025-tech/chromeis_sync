import time
import frappe

from chromeis_sync.level5.reconciliation.payment_registry import (
    PaymentRegistryWriter,
)


class PaymentPopulationRunner:

    @staticmethod
    def run(start_after=None, limit=None, delay=0.25):

        payments = frappe.db.sql("""
            SELECT name
            FROM `tabPayment Entry`
            WHERE docstatus IN (1, 2)
              AND (%s IS NULL OR name > %s)
            ORDER BY name
            LIMIT %s
        """, (start_after, start_after, limit or 100000), pluck="name")

        total = len(payments)

        summary = {
            "total": total,
            "processed": 0,
            "verified": 0,
            "cancelled_reversal": 0,
            "exceptions": 0,
            "failed": 0,
            "last_processed": None,
        }

        for index, payment_name in enumerate(payments, start=1):

            try:
                written = PaymentRegistryWriter.run(
                    [payment_name]
                )

                for row in written:

                    status = row.get("status")

                    if status == "VERIFIED":
                        summary["verified"] += 1

                    elif status == "CANCELLED_REVERSAL":
                        summary["cancelled_reversal"] += 1

                    else:
                        summary["exceptions"] += 1

                summary["processed"] += 1
                summary["last_processed"] = payment_name

            except Exception as exc:

                summary["failed"] += 1
                summary["last_processed"] = payment_name

                print(
                    f"[LEVEL5 PAYMENT ERROR] "
                    f"{payment_name}: {exc}"
                )

            if index % 25 == 0:
                frappe.db.commit()

                print(
                    f"[LEVEL5 PAYMENT] "
                    f"{index}/{total} | "
                    f"Verified={summary['verified']} | "
                    f"Reversal={summary['cancelled_reversal']} | "
                    f"Exceptions={summary['exceptions']} | "
                    f"Failed={summary['failed']}"
                )

            if delay:
                time.sleep(delay)

        frappe.db.commit()

        print("\nLEVEL 5 PAYMENT RUN COMPLETE")
        print(summary)

        return summary
