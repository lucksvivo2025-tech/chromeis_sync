import frappe

from chromeis_sync.migration_audit.models import RepairCandidate


class RepairCandidateAnalyzer:

    def analyze(self, invoice_name):

        invoice = frappe.get_doc("Sales Invoice", invoice_name)

        candidate = RepairCandidate(
            invoice_name=invoice.name,
            whmcs_invoice_id=invoice.whmcs_invoice_id or "",
            currency=invoice.currency,
            target_currency=invoice.currency,
            submitted=(invoice.docstatus == 1),
            conversion_rate=float(invoice.conversion_rate or 0),
        )

        # --------------------------------------------------
        # Skip non-submitted invoices
        # --------------------------------------------------

        if invoice.docstatus != 1:
            candidate.status = "SKIP"
            candidate.reasons.append("Invoice is not submitted")
            return candidate

        # --------------------------------------------------
        # GL Status
        # --------------------------------------------------

        gl_count = frappe.db.count(
            "GL Entry",
            {
                "voucher_no": invoice.name
            }
        )

        candidate.has_gl = gl_count > 0

        # --------------------------------------------------
        # WHMCS Currency Validation
        # --------------------------------------------------

        whmcs_currency = frappe.db.sql(
            """
            SELECT cur.code
            FROM whmcs_mirror.tblinvoices i
            JOIN whmcs_mirror.tblclients c
                ON c.id = i.userid
            JOIN whmcs_mirror.tblcurrencies cur
                ON cur.id = c.currency
            WHERE i.id = %s
            """,
            (invoice.whmcs_invoice_id,),
            as_dict=True,
        )

        if whmcs_currency:

            whmcs_currency = whmcs_currency[0]["code"]

            if (
                invoice.currency == "PKR"
                and whmcs_currency == "USD"
                and float(invoice.conversion_rate or 0) == 1.0
            ):

                candidate.status = "REPAIR"
                candidate.repair_required = True
                candidate.target_currency = "USD"

                candidate.reasons.append(
                    "ERP currency differs from WHMCS currency"
                )

                return candidate

        # --------------------------------------------------
        # Existing Currency Validation
        # --------------------------------------------------

        if candidate.currency == "PKR":

            if candidate.conversion_rate <= 0:
                candidate.status = "REPAIR"
                candidate.repair_required = True
                candidate.reasons.append(
                    "Invalid PKR conversion rate"
                )
                return candidate

        elif candidate.currency == "USD":

            if round(candidate.conversion_rate, 6) != 1:
                candidate.status = "REPAIR"
                candidate.repair_required = True
                candidate.reasons.append(
                    "Unexpected USD conversion rate"
                )
                return candidate

        # --------------------------------------------------
        # Missing GL Analysis
        # --------------------------------------------------

        if not candidate.has_gl:

            if abs(float(invoice.base_grand_total or 0)) < 0.01:

                candidate.status = "INFO"
                candidate.expected_no_gl = True

                candidate.reasons.append(
                    "No GL expected (base amount rounds to zero)"
                )

                return candidate

            candidate.status = "REPAIR"
            candidate.repair_required = True

            candidate.reasons.append(
                "Missing GL Entries"
            )

            return candidate

        return candidate

    def analyze_all(self):

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["is", "set"]
            },
            pluck="name"
        )

        results = []

        for invoice_name in invoices:
            results.append(
                self.analyze(invoice_name)
            )

        return results
