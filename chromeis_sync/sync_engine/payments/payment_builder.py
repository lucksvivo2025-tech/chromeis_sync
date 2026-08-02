import frappe


class PaymentBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def _mode_of_payment(self):
        gateway = (self.snapshot.get("gateway") or "").lower()

        mapping = {
            "banktransfer": "Bank Transfer",
            "paypal": "PayPal",
            "stripe": "Stripe",
            "skrill": "Skrill",
            "wise": "Wise",
            "alfalah": "Bank Transfer",
            "hbl": "HBL",
            "meezan": "Meezan",
            "creditcard": "Credit Card",
            "mailin": "Cheque",
        }

        return mapping.get(gateway, "WHMCS Manual")

    def build(self):

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(self.snapshot["invoiceid"])
            },
            "name",
        )

        if not invoice:
            raise Exception(
                f"ERP Invoice not found for WHMCS Invoice {self.snapshot['invoiceid']}"
            )

        invoice_doc = frappe.get_doc("Sales Invoice", invoice)

        customer = invoice_doc.customer

        if not customer:
            raise Exception(
                f"Customer not found on ERP Invoice {invoice}"
            )

        payment = frappe.new_doc("Payment Entry")

        payment.payment_type = "Receive"
        payment.party_type = "Customer"
        payment.party = customer
        payment.company = "Chromeis Pvt Ltd"

        payment.posting_date = self.snapshot["date"].date()
        payment.mode_of_payment = self._mode_of_payment()

        payment.paid_from = invoice_doc.debit_to
        payment.paid_to = "WHMCS USD Clearing - CPL"

        payment.paid_from_account_currency = "USD"
        payment.paid_to_account_currency = "USD"

        payment_amount = float(self.snapshot.get("amountin") or 0)

        payment.paid_amount = payment_amount
        payment.received_amount = payment_amount

        payment.reference_no = (
            self.snapshot.get("transid")
            or str(self.snapshot["id"])
        )

        payment.reference_date = self.snapshot["date"].date()

        allocated = min(
            payment_amount,
            max(float(invoice_doc.outstanding_amount or 0), 0),
        )

        payment.append(
            "references",
            {
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice,
                "total_amount": float(invoice_doc.grand_total or 0),
                "outstanding_amount": max(
                    float(invoice_doc.outstanding_amount or 0), 0
                ),
                "allocated_amount": allocated,
            },
        )

        return payment
