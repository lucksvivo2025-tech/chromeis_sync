import frappe

from chromeis_sync.level5.api.client import Level5WHMCSClient
from chromeis_sync.level5.identity.payment_identity import PaymentIdentityResolver


class PaymentVerifier:

    @staticmethod
    def verify(payment_name):

        identity = PaymentIdentityResolver.resolve(payment_name)

        result = {
            "erp_id": payment_name,
            "whmcs_record_id": identity["whmcs_record_id"],
            "whmcs_invoice_id": identity["whmcs_invoice_id"],
            "whmcs_customer_id": identity["whmcs_customer_id"],
            "erp_docstatus": identity["docstatus"],
            "status": "PENDING",
            "differences": [],
        }

        if not identity["mirror_found"]:
            result["status"] = "MISSING_IN_WHMC_MIRROR"
            return result

        invoice_id = identity["whmcs_invoice_id"]

        if not invoice_id:
            result["status"] = "MISSING_WHMC_INVOICE_ID"
            return result

        client = Level5WHMCSClient()
        api_invoice = client.get_invoice(invoice_id)

        transactions = api_invoice.get("transactions", {}).get(
            "transaction", []
        )

        if isinstance(transactions, dict):
            transactions = [transactions]

        whmcs_payment = None

        for txn in transactions:
            if str(txn.get("id")) == str(
                identity["whmcs_record_id"]
            ):
                whmcs_payment = txn
                break

        if not whmcs_payment:
            result["differences"].append(
                "WHMCS payment record not found in API invoice"
            )

        erp_amount = float(identity["amount"] or 0)

        api_amount = 0.0

        if whmcs_payment:
            api_amount = float(
                whmcs_payment.get("amountin") or 0
            )

        mirror_amount = float(
            identity["mirror"].get("amountin") or 0
        )

        # ---------------------------------------------------------
        # Cancelled ERP payment = reversal, not additional payment
        # ---------------------------------------------------------

        if identity["docstatus"] == 2:

            reversal_entries = frappe.db.sql("""
                SELECT
                    debit,
                    credit
                FROM `tabGL Entry`
                WHERE voucher_no=%s
                  AND remarks LIKE %s
            """, (
                payment_name,
                "%On cancellation%",
            ), as_dict=True)

            if not reversal_entries:
                result["differences"].append(
                    "Cancelled ERP payment has no cancellation GL reversal"
                )

            result["status"] = (
                "CANCELLED_REVERSAL"
                if not result["differences"]
                else "VERIFIED_WITH_EXCEPTION"
            )

        else:

            if round(erp_amount, 2) != round(api_amount, 2):
                result["differences"].append(
                    f"ERP amount {erp_amount} != API amount {api_amount}"
                )

            if round(mirror_amount, 2) != round(api_amount, 2):
                result["differences"].append(
                    f"Mirror amount {mirror_amount} != API amount {api_amount}"
                )

            if not result["differences"]:
                result["status"] = "VERIFIED"
            else:
                result["status"] = "VERIFIED_WITH_EXCEPTION"

        result["api_amount"] = api_amount
        result["mirror_amount"] = mirror_amount
        result["erp_amount"] = erp_amount
        result["api_status"] = api_invoice.get("status")
        result["api_balance"] = float(
            api_invoice.get("balance") or 0
        )

        return result
