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

                a.invoiceid AS whmcs_invoice_id,

                si.name AS sales_invoice,
                si.customer,
                si.grand_total,
                si.outstanding_amount,

                (
                    SELECT COUNT(*)
                    FROM whmcs_mirror.tblaccounts a2
                    WHERE
                        a2.invoiceid = a.invoiceid
                        AND a2.amountin > 0
                ) AS positive_payment_count,

                (
                    SELECT COUNT(*)
                    FROM whmcs_mirror.tblaccounts a2
                    WHERE
                        a2.invoiceid = a.invoiceid
                        AND a2.amountout > 0
                ) AS refund_count,

                (
                    SELECT COUNT(*)
                    FROM `tabPayment Entry Reference`
                    WHERE parent = pe.name
                ) AS reference_count

            FROM `tabPayment Entry` pe

            INNER JOIN whmcs_mirror.tblaccounts a
                ON a.id = CAST(pe.custom_whmcs_txn_id AS UNSIGNED)

            LEFT JOIN `tabSales Invoice` si
                ON si.whmcs_invoice_id = a.invoiceid

            WHERE
                pe.docstatus = 1
                AND pe.unallocated_amount = pe.paid_amount

            ORDER BY pe.name
            """,
            as_dict=True,
        )

    def execute(self):

        print()
        print("=" * 80)
        print("PAYMENT REPAIR PLANNER")
        print("=" * 80)

        rows = self.get_candidates()

        print(f"Broken Payment Entries : {len(rows)}")
        print()

        safe = 0
        refunds = 0
        skipped = 0

        for row in rows:

            if row.reference_count > 0:
                skipped += 1
                continue

            if row.refund_count > 0:
                refunds += 1
            else:
                safe += 1

        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Safe candidates     : {safe}")
        print(f"Refund candidates   : {refunds}")
        print(f"Skipped             : {skipped}")
        print(f"Total               : {len(rows)}")
