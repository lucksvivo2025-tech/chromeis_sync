import frappe


class MigrationCompleteness:

    def build(self):

        whmcs_invoices = frappe.db.sql("""
            SELECT
                id,
                userid,
                status,
                total,
                date,
                datepaid
            FROM whmcs_mirror.tblinvoices
            ORDER BY id
        """, as_dict=True)

        report = []

        for whmcs in whmcs_invoices:

            erp = frappe.db.sql("""
                SELECT
                    name,
                    docstatus,
                    customer,
                    posting_date,
                    grand_total,
                    whmcs_invoice_id
                FROM `tabSales Invoice`
                WHERE whmcs_invoice_id=%s
                LIMIT 1
            """, whmcs["id"], as_dict=True)

            row = {
                "whmcs_invoice_id": str(whmcs["id"]),
                "whmcs_status": whmcs["status"],
                "customer_id": whmcs["userid"],
                "total": float(whmcs["total"] or 0),
                "date": whmcs["date"],
                "datepaid": whmcs["datepaid"],
                "erp_invoice": None,
                "erp_docstatus": None,
                "migration_status": "",
            }

            if not erp:

                row["migration_status"] = "MISSING"

            else:

                invoice = erp[0]

                row["erp_invoice"] = invoice["name"]
                row["erp_docstatus"] = invoice["docstatus"]

                if invoice["docstatus"] == 1:
                    row["migration_status"] = "MIGRATED"

                elif invoice["docstatus"] == 2:
                    row["migration_status"] = "CANCELLED"

                else:
                    row["migration_status"] = "DRAFT"

            report.append(row)

        return report

    def summary(self):

        report = self.build()

        total = len(report)

        migrated = sum(
            1 for r in report
            if r["migration_status"] == "MIGRATED"
        )

        missing = sum(
            1 for r in report
            if r["migration_status"] == "MISSING"
        )

        cancelled = sum(
            1 for r in report
            if r["migration_status"] == "CANCELLED"
        )

        draft = sum(
            1 for r in report
            if r["migration_status"] == "DRAFT"
        )

        paid_missing = sum(
            1
            for r in report
            if (
                r["migration_status"] == "MISSING"
                and r["whmcs_status"] == "Paid"
            )
        )

        print("=" * 60)
        print("Migration Completeness Summary")
        print("=" * 60)
        print(f"WHMCS Invoices     : {total}")
        print(f"Migrated           : {migrated}")
        print(f"Missing            : {missing}")
        print(f"Cancelled          : {cancelled}")
        print(f"Draft              : {draft}")
        print(f"Missing Paid       : {paid_missing}")
        print("=" * 60)

        return report

    def missing(self):

        return [
            r
            for r in self.build()
            if r["migration_status"] == "MISSING"
        ]

    def missing_paid(self):

        return [
            r
            for r in self.build()
            if (
                r["migration_status"] == "MISSING"
                and r["whmcs_status"] == "Paid"
            )
        ]
