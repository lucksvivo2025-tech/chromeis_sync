import frappe


class PaymentReferenceParity:

    def execute(self):

        print()
        print("=" * 80)
        print("PAYMENT REFERENCE PARITY")
        print("=" * 80)

        result = frappe.db.sql("""
            SELECT
                COUNT(*) AS reference_count,
                ROUND(SUM(allocated_amount), 2) AS allocated
            FROM `tabPayment Entry Reference`
        """, as_dict=True)[0]

        submitted = frappe.db.sql("""
            SELECT
                COUNT(*) AS submitted_references,
                ROUND(SUM(per.allocated_amount), 2) AS allocated
            FROM `tabPayment Entry Reference` per
            JOIN `tabPayment Entry` pe
                ON pe.name = per.parent
            WHERE
                pe.docstatus = 1
        """, as_dict=True)[0]

        cancelled = frappe.db.sql("""
            SELECT
                COUNT(*) AS cancelled_references,
                ROUND(SUM(per.allocated_amount), 2) AS allocated
            FROM `tabPayment Entry Reference` per
            JOIN `tabPayment Entry` pe
                ON pe.name = per.parent
            WHERE
                pe.docstatus = 2
        """, as_dict=True)[0]

        overallocated = frappe.db.sql("""
            SELECT
                COUNT(*) AS overallocated
            FROM `tabPayment Entry Reference` per
            JOIN `tabPayment Entry` pe
                ON pe.name = per.parent
            WHERE
                pe.docstatus = 1
                AND per.allocated_amount > per.total_amount
        """, as_dict=True)[0]

        print(f"Total References      : {result.reference_count}")
        print(f"Allocated Amount      : {result.allocated:,.2f}")

        print()

        print(f"Submitted References  : {submitted.submitted_references}")
        print(f"Submitted Allocated   : {submitted.allocated:,.2f}")

        print()

        print(f"Cancelled References  : {cancelled.cancelled_references}")
        print(f"Cancelled Allocated   : {cancelled.allocated:,.2f}")

        print()

        print(f"Overallocated         : {overallocated.overallocated}")

        print()

        if overallocated.overallocated == 0:
            print("PASS")
        else:
            print("FAIL")
