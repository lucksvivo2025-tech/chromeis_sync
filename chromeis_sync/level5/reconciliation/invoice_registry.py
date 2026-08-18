import frappe


class InvoiceRegistryWriter:

    @staticmethod
    def write(result, identity_classification=None):

        erp_id = result.get("erp_id")
        whmcs_id = result.get("whmcs_id")

        existing = frappe.db.get_value(
            "WHMCS Level 5 Identity Registry",
            {
                "entity_type": "Invoice",
                "erp_id": erp_id,
            },
            "name",
        )

        if existing:
            doc = frappe.get_doc(
                "WHMCS Level 5 Identity Registry",
                existing,
            )
        else:
            doc = frappe.new_doc(
                "WHMCS Level 5 Identity Registry"
            )

        doc.entity_type = "Invoice"
        doc.whmcs_id = str(whmcs_id or "")
        doc.whmcs_record_id = str(whmcs_id or "")
        doc.erp_doctype = "Sales Invoice"
        doc.erp_id = erp_id

        doc.parent_whmcs_id = ""
        doc.parent_erp_id = ""

        doc.human_reference = (
            f"INV-{whmcs_id}-ERP-{erp_id}"
        )

        # Identity classification

        doc.classification = (
            result.get("identity_classification")
            or identity_classification
            or ""
        )

        verification_result = result.get("status")

        if identity_classification == "CANCELLED_REVERSED":
            doc.verification_status = "Pending"

        elif identity_classification == "MISSING":
            doc.verification_status = "Missing in ERP"

        elif identity_classification == "ORPHAN":
            doc.verification_status = "Missing in WHMCS"

        elif identity_classification in (
            "DUPLICATE",
            "UNRESOLVED",
        ):
            doc.verification_status = "Pending"

        elif verification_result == "VERIFIED":
            doc.verification_status = "Verified"

        elif verification_result == "ERP_DIFFERENCE":
            doc.verification_status = "ERP Difference"

        else:
            doc.verification_status = "Pending"

        doc.verification_result = verification_result

        # Reconciliation classification

        doc.reconciliation_classification = (
            result.get("reconciliation_classification")
            or ""
        )

        differences = result.get("differences") or []

        for difference in differences:

            if difference.get("field") != "credit_invoice_allocation":
                continue

            doc.whmcs_credit_id = str(
                difference.get("whmcs_credit_id") or ""
            )

            doc.whmcs_credit_amount = difference.get(
                "whmcs_amount"
            )

            doc.erp_credit_journal = str(
                difference.get("erp_journal_entry") or ""
            )

            doc.erp_credit_amount = difference.get(
                "erp_credit_amount"
            )

            doc.invoice_allocation_status = (
                "NOT_ALLOCATED"
                if not difference.get(
                    "invoice_allocation_found"
                )
                else "ALLOCATED"
            )

        if not any(
            d.get("field") == "credit_invoice_allocation"
            for d in differences
        ):
            doc.invoice_allocation_status = "NOT_APPLICABLE"

        doc.last_verified = frappe.utils.now_datetime()

        doc.verification_run = (
            f"INVOICE-{frappe.utils.now_datetime()}"
        )

        doc.notes = "\n".join(
            str(item)
            for item in differences
        )

        doc.save(ignore_permissions=True)

        return doc.name
