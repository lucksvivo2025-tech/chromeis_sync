import frappe


class PaymentIdentityResolver:

    @staticmethod
    def resolve(payment_name):

        payment = frappe.get_doc("Payment Entry", payment_name)

        # ---------------------------------------------------------
        # WHMCS payment identity
        #
        # Prefer the explicit ERP WHMCS transaction ID.
        # reference_no is only a legacy/fallback identity.
        # ---------------------------------------------------------

        record_id = None

        explicit_txn_id = payment.get("custom_whmcs_txn_id")

        if explicit_txn_id:
            record_id = str(explicit_txn_id).strip()

        elif payment.reference_no:
            ref = str(payment.reference_no).strip()

            if ref.startswith("WHMCS-"):
                record_id = ref.replace("WHMCS-", "", 1).strip()

        mirror = None

        if record_id:
            rows = frappe.db.sql("""
                SELECT
                    id,
                    userid,
                    invoiceid,
                    amountin,
                    amountout,
                    fees,
                    transid,
                    date
                FROM whmcs_mirror.tblaccounts
                WHERE id=%s
                LIMIT 1
            """, (record_id,), as_dict=True)

            if rows:
                mirror = rows[0]

        whmcs_invoice_id = None
        whmcs_customer_id = None
        transaction_id = None
        erp_invoice_id = None

        if mirror:
            whmcs_invoice_id = mirror.get("invoiceid")
            whmcs_customer_id = mirror.get("userid")
            transaction_id = mirror.get("transid") or None

        if whmcs_invoice_id is not None:
            erp_invoice_id = frappe.db.get_value(
                "Sales Invoice",
                {"whmcs_invoice_id": str(whmcs_invoice_id)},
                "name",
            )

        human_reference = (
            f"PAY-{payment.posting_date.year}-{record_id}"
            if record_id
            else payment.name
        )

        return {
            "erp_id": payment.name,
            "erp_invoice_id": erp_invoice_id,
            "whmcs_record_id": str(record_id) if record_id else None,
            "whmcs_transaction_id": transaction_id,
            "whmcs_invoice_id": (
                str(whmcs_invoice_id)
                if whmcs_invoice_id is not None
                else None
            ),
            "whmcs_customer_id": (
                str(whmcs_customer_id)
                if whmcs_customer_id is not None
                else None
            ),
            "human_reference": human_reference,
            "customer": payment.party,
            "amount": float(payment.paid_amount or 0),
            "posting_date": str(payment.posting_date),
            "docstatus": payment.docstatus,
            "mirror_found": bool(mirror),
            "mirror": mirror,
        }
