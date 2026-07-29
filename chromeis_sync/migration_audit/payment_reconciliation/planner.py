import frappe

from .models import PaymentReconciliationCandidate


class PaymentReconciliationPlanner:

    def execute(self):

        rows = frappe.db.sql(
            """
            SELECT

                a.id                         AS whmcs_account_id,
                a.invoiceid                  AS whmcs_invoice_id,
                a.transid                    AS whmcs_transaction_id,
                a.userid                     AS whmcs_customer_id,
                a.date                       AS whmcs_payment_date,
                a.amountin                   AS whmcs_amount,
                a.amountout                  AS whmcs_refund_amount,

                pe.name                      AS payment_entry,
                pe.party                     AS customer,
                pe.paid_amount,
                pe.unallocated_amount,

                si_expected.name             AS expected_sales_invoice,
                si_expected.outstanding_amount,

                si_allocated.name            AS allocated_sales_invoice,

                (
                    SELECT COUNT(*)
                    FROM `tabPayment Entry Reference` per2
                    WHERE per2.parent = pe.name
                      AND per2.reference_doctype = 'Sales Invoice'
                ) AS reference_count

            FROM whmcs_mirror.tblaccounts a

            LEFT JOIN `tabPayment Entry` pe
                ON pe.custom_whmcs_txn_id = CAST(a.id AS CHAR)

            LEFT JOIN `tabPayment Entry Reference` per
                ON per.parent = pe.name
                AND per.reference_doctype = 'Sales Invoice'

            LEFT JOIN `tabSales Invoice` si_allocated
                ON si_allocated.name = per.reference_name

            LEFT JOIN `tabSales Invoice` si_expected
                ON si_expected.whmcs_invoice_id = CAST(a.invoiceid AS CHAR)

            WHERE
                a.amountin > 0
                AND a.invoiceid > 0

            ORDER BY a.id
            """,
            as_dict=True,
        )

        candidates = []

        for row in rows:

            candidates.append(
                PaymentReconciliationCandidate(
                    whmcs_account_id=row.whmcs_account_id,
                    whmcs_invoice_id=row.whmcs_invoice_id,
                    whmcs_transaction_id=row.whmcs_transaction_id or "",
                    whmcs_customer_id=row.whmcs_customer_id,
                    whmcs_payment_date=str(row.whmcs_payment_date),
                    whmcs_amount=float(row.whmcs_amount),
                    whmcs_refund_amount=float(row.whmcs_refund_amount),

                    payment_entry=row.payment_entry,
                    expected_sales_invoice=row.expected_sales_invoice,
                    allocated_sales_invoice=row.allocated_sales_invoice,
                    customer=row.customer,

                    paid_amount=float(row.paid_amount or 0),
                    unallocated_amount=float(row.unallocated_amount or 0),
                    outstanding_amount=float(row.outstanding_amount or 0),

                    reference_count=row.reference_count,
                )
            )

        return candidates
