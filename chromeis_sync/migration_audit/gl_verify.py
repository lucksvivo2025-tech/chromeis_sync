import frappe

from chromeis_sync.migration_audit.models import VerificationResult


class GLVerifier:

    def verify(self, snapshot, new_invoice):

        result = VerificationResult()

        old_gl = sorted(
            snapshot["gl_entries"],
            key=lambda x: (x["account"], x["debit"], x["credit"])
        )

        new_gl = frappe.db.sql("""
            SELECT
                account,
                debit,
                credit
            FROM `tabGL Entry`
            WHERE voucher_no=%s
            ORDER BY account
        """, new_invoice.name, as_dict=True)

        new_gl = sorted(
            new_gl,
            key=lambda x: (x["account"], x["debit"], x["credit"])
        )

        if len(old_gl) != len(new_gl):
            result.passed = False
            result.errors.append(
                "GL row count mismatch"
            )
            return result

        for index, (old_row, new_row) in enumerate(zip(old_gl, new_gl), start=1):

            for field in ("account", "debit", "credit"):

                if old_row[field] != new_row[field]:
                    result.passed = False
                    result.errors.append(
                        f"GL Row {index}: {field} mismatch "
                        f"({old_row[field]} != {new_row[field]})"
                    )

        return result
