import frappe


class PaymentRepairPlanner:

    def get_candidates(self):
        return frappe.db.sql(
            """
            SELECT

                pe.name AS payment_entry,
                pe.party,
                pe.paid_amount,
                pe.unallocated_amount,
                pe.custom_whmcs_txn_id,

                si.name AS sales_invoice,
                si.customer,
                si.grand_total,
                si.outstanding_amount,

                per.name AS payment_reference,
                per.total_amount,
                per.outstanding_amount AS reference_outstanding,
                per.allocated_amount

            FROM `tabPayment Entry Reference` per

            INNER JOIN `tabPayment Entry` pe
                ON pe.name = per.parent

            INNER JOIN `tabSales Invoice` si
                ON si.name = per.reference_name

            WHERE
                pe.docstatus = 1
                AND si.docstatus = 1
                AND per.allocated_amount > per.total_amount

            ORDER BY pe.name
            """,
            as_dict=True,
        )

    def execute(self):

        rows = self.get_candidates()

        print()
        print("=" * 80)
        print("ALLOCATION REPAIR PLANNER")
        print("=" * 80)
        print(f"Repairable Allocations : {len(rows)}")
