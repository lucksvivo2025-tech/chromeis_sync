import frappe

from chromeis_sync.migration_audit.models import VerificationResult


class CommercialGLVerifier:

    def verify(self, snapshot, new_invoice):

        result = VerificationResult()

        new_gl = frappe.db.sql("""
            SELECT
                account,
                debit,
                credit
            FROM `tabGL Entry`
            WHERE voucher_no=%s
            ORDER BY account
        """, new_invoice.name, as_dict=True)

        # Remove zero-value rows
        new_gl = [
            row
            for row in new_gl
            if round(float(row["debit"]), 2) != 0
            or round(float(row["credit"]), 2) != 0
        ]

        # Ignore round off account
        new_gl = [
            row
            for row in new_gl
            if row["account"] != "Round Off - CPL"
        ]

        if not new_gl:
            result.passed = False
            result.errors.append("No GL entries generated.")
            return result

        # ----------------------------------------------------
        # Check GL is balanced
        # ----------------------------------------------------

        total_debit = round(
            sum(float(r["debit"]) for r in new_gl),
            2,
        )

        total_credit = round(
            sum(float(r["credit"]) for r in new_gl),
            2,
        )

        if total_debit != total_credit:
            result.passed = False
            result.errors.append(
                f"GL not balanced (Debit={total_debit}, Credit={total_credit})"
            )

        # ----------------------------------------------------
        # Check Debtors
        # ----------------------------------------------------

        debtors = [
            row
            for row in new_gl
            if row["account"] == "Debtors - CPL"
        ]

        if len(debtors) != 1:
            result.passed = False
            result.errors.append(
                "Expected exactly one Debtors GL entry."
            )
        else:
            debtor_amount = round(
                float(debtors[0]["debit"]),
                2,
            )

            expected = round(
                float(new_invoice.grand_total),
                2,
            )

            if debtor_amount != expected:
                result.passed = False
                result.errors.append(
                    f"Debtors amount mismatch ({debtor_amount} != {expected})"
                )

        # ----------------------------------------------------
        # Revenue check
        # ----------------------------------------------------

        revenue_accounts = (
            "Sales - ",
            "Customer Deposits - ",
        )

        revenue_credit = round(
            sum(
                float(r["credit"])
                for r in new_gl
                if any(
                    r["account"].startswith(prefix)
                    for prefix in revenue_accounts
                )
            ),
            2,
        )

        expected_revenue = round(
            float(new_invoice.net_total),
            2,
        )

        if revenue_credit != expected_revenue:
            result.passed = False
            result.errors.append(
                f"Revenue mismatch ({revenue_credit} != {expected_revenue})"
            )

        # ----------------------------------------------------
        # GST check
        # ----------------------------------------------------

        tax = round(
            float(new_invoice.total_taxes_and_charges or 0),
            2,
        )

        gst_exists = any(
            row["account"] == "GST - CPL"
            for row in new_gl
        )

        if tax > 0 and not gst_exists:
            result.passed = False
            result.errors.append(
                "GST GL entry missing."
            )

        if tax == 0 and gst_exists:
            result.passed = False
            result.errors.append(
                "Unexpected GST GL entry."
            )

        return result
