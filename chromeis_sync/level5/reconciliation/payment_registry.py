import frappe

from chromeis_sync.level5.reconciliation.payment_runner import (
    PaymentVerificationRunner,
)


class PaymentRegistryWriter:

    @staticmethod
    def write(result):

        erp_id = result["erp_id"]
        whmcs_id = result.get("whmcs_record_id")

        existing = frappe.db.get_value(
            "WHMCS Level 5 Identity Registry",
            {
                "entity_type": "Payment",
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

        doc.entity_type = "Payment"
        doc.whmcs_id = str(whmcs_id or "")
        doc.whmcs_record_id = str(whmcs_id or "")
        doc.erp_doctype = "Payment Entry"
        doc.erp_id = erp_id

        doc.parent_whmcs_id = str(
            result.get("whmcs_invoice_id") or ""
        )

        doc.parent_erp_id = ""

        doc.human_reference = (
            f"PAY-{result.get('whmcs_invoice_id')}-"
            f"{whmcs_id}-ERP-{erp_id}"
        )

        doc.verification_status = (
            "Verified"
            if result["status"] == "VERIFIED"
            else "Verified With Exception"
        )

        doc.verification_result = result["status"]

        doc.api_amount = result.get("api_amount")
        doc.mirror_amount = result.get("mirror_amount")
        doc.erp_amount = result.get("erp_amount")
        doc.api_status = result.get("api_status")
        doc.api_balance = result.get("api_balance")

        doc.last_verified = frappe.utils.now_datetime()

        doc.verification_run = (
            f"PAYMENT-{frappe.utils.now_datetime()}"
        )

        doc.notes = "\n".join(
            result.get("differences") or []
        )

        doc.save(ignore_permissions=True)

        return doc.name


    @classmethod
    def run(cls, payment_names):

        results = PaymentVerificationRunner.run(
            payment_names
        )

        written = []

        for result in results:

            name = cls.write(result)

            written.append({
                "registry": name,
                "erp_id": result["erp_id"],
                "status": result["status"],
            })

        frappe.db.commit()

        return written
