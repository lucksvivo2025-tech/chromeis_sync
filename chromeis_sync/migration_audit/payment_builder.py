import frappe


class PaymentBuilder:

    GATEWAY_MAP = {
        "banktransfer": {
            "mode_of_payment": "Bank Transfer",
            "paid_to": "Bank Accounts - CPL - CPL",
        },
        "paypal": {
            "mode_of_payment": "PayPal",
            "paid_to": "PayPal - USD Account - CPL",
        },
        "alfalah": {
            "mode_of_payment": "Bank Transfer",
            "paid_to": "Bank Accounts - CPL - CPL",
        },
        "moneybookers": {
            "mode_of_payment": "Skrill",
            "paid_to": "Skrill - CPL",
        },
        "": {
            "mode_of_payment": "Bank Transfer",
            "paid_to": "Bank Accounts - CPL - CPL",
        },
    }

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.payment = snapshot["payment"]
        self.invoice = snapshot["invoice"]

    def build(self):

        pe = frappe.new_doc("Payment Entry")

        pe.payment_type = "Receive"
        pe.company = "Chromeis Pvt Ltd"
        pe.party_type = "Customer"

        if self.invoice:
            pe.party = self.invoice["customer"]
        else:
            pe.party = f"WH-CUST-{self.payment['userid']}"

        # --------------------------------------------------
        # Posting Date / Reference Date
        # --------------------------------------------------

        posting_date = self.payment.get("date")

        if not posting_date and self.invoice:
            posting_date = self.invoice.get("posting_date")

        if not posting_date:
            posting_date = frappe.utils.nowdate()

        pe.posting_date = posting_date
        pe.reference_date = posting_date

        # --------------------------------------------------
        # Reference Number
        # --------------------------------------------------

        transid = (self.payment.get("transid") or "").strip()

        if not transid:
            transid = f"WHMCS-{self.payment['id']}"

        if len(transid) > 140:
            transid = transid[:140]

        pe.reference_no = transid

        # --------------------------------------------------
        # Store Original WHMCS IDs
        # --------------------------------------------------

        pe.custom_whmcs_txn_id = str(self.payment["id"])

        if self.payment.get("refundid"):
            pe.custom_whmcs_credit_id = str(self.payment["refundid"])

        # --------------------------------------------------
        # Gateway
        # --------------------------------------------------

        gateway = (self.payment.get("gateway") or "").lower()

        mapping = self.GATEWAY_MAP.get(
            gateway,
            self.GATEWAY_MAP[""]
        )

        pe.mode_of_payment = mapping["mode_of_payment"]
        pe.paid_from = "Debtors - CPL"
        pe.paid_to = mapping["paid_to"]

        currency = (
            self.invoice["currency"]
            if self.invoice
            else "USD"
        )

        pe.paid_from_account_currency = currency
        pe.paid_to_account_currency = currency

        amount = float(self.payment.get("amountin") or 0)

        pe.paid_amount = amount
        pe.received_amount = amount

        pe.source_exchange_rate = 1
        pe.target_exchange_rate = 1

        # --------------------------------------------------
        # Allocate Invoice
        # --------------------------------------------------

        if self.invoice:

            outstanding = float(
                self.invoice.get("outstanding_amount") or 0
            )

            if outstanding > 0:

                pe.append(
                    "references",
                    {
                        "reference_doctype": "Sales Invoice",
                        "reference_name": self.invoice["name"],
                        "allocated_amount": min(
                            outstanding,
                            amount,
                        ),
                    },
                )

        return pe
