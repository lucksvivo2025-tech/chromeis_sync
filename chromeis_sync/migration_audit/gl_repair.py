import frappe


class GLRepair:

    def __init__(self, invoice_name):
        self.invoice_name = invoice_name

    def get_cost_center(self):

        rows = frappe.db.sql("""
            SELECT DISTINCT cost_center
            FROM `tabSales Invoice Item`
            WHERE
                parent=%s
                AND IFNULL(cost_center,'')<>''
        """, self.invoice_name, as_dict=True)

        if len(rows) != 1:
            raise Exception(
                f"{self.invoice_name} has {len(rows)} cost centers."
            )

        return rows[0]["cost_center"]

    def repair(self, dry_run=True):

        cost_center = self.get_cost_center()

        gl_rows = frappe.db.sql("""
            SELECT
                name,
                account,
                cost_center
            FROM `tabGL Entry`
            WHERE
                voucher_type='Sales Invoice'
                AND voucher_no=%s
                AND IFNULL(cost_center,'')=''
            ORDER BY creation
        """, self.invoice_name, as_dict=True)

        print(f"\nInvoice : {self.invoice_name}")
        print(f"Cost Center : {cost_center}")
        print(f"Rows : {len(gl_rows)}")

        if dry_run:

            print("\nDRY RUN\n")

            for row in gl_rows:
                print(
                    row["name"],
                    "->",
                    cost_center
                )

            return len(gl_rows)

        updated = 0

        for row in gl_rows:

            frappe.db.set_value(
                "GL Entry",
                row["name"],
                "cost_center",
                cost_center,
                update_modified=False
            )

            updated += 1

        frappe.db.commit()

        print(f"\nUpdated {updated} GL Entries")

        return updated
