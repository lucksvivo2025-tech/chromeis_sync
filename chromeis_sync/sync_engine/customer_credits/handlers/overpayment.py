import frappe


class OverpaymentHandler:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        invoice = None

        if self.snapshot["relid"]:

            invoice = frappe.db.get_value(
                "Sales Invoice",
                {
                    "whmcs_invoice_id": str(self.snapshot["relid"])
                },
                ["name", "customer", "debit_to"],
                as_dict=True,
            )

            if not invoice:
                raise Exception(
                    f"ERP Invoice not found for WHMCS Invoice {self.snapshot['relid']}"
                )

        else:

            customer = frappe.db.get_value(
                "Customer",
                {
                    "custom_whmcs_user_id": str(self.snapshot["clientid"])
                },
                "name",
            )

            if not customer:
                raise Exception(
                    f"ERP Customer not found for WHMCS Client {self.snapshot['clientid']}"
                )

            invoice = frappe._dict(
                {
                    "customer": customer,
                    "debit_to": "Debtors - CPL",
                }
            )

        journal = frappe.new_doc("Journal Entry")

        journal.voucher_type = "Journal Entry"
        journal.company = "Chromeis Pvt Ltd"
        journal.posting_date = self.snapshot["date"]

        journal.user_remark = (
            self.snapshot.get("description")
            or f"WHMCS Credit #{self.snapshot['id']}"
        )

        journal.custom_whmcs_credit_id = str(self.snapshot["id"])

        amount = float(self.snapshot.get("amount") or 0)

        if amount >= 0:

            journal.append(
                "accounts",
                {
                    "account": "Customer Deposits - CPL",
                    "credit_in_account_currency": amount,
                },
            )

            row = {
                "account": invoice.debit_to,
                "party_type": "Customer",
                "party": invoice.customer,
                "debit_in_account_currency": amount,
            }

        else:

            amount = abs(amount)

            journal.append(
                "accounts",
                {
                    "account": "Customer Deposits - CPL",
                    "debit_in_account_currency": amount,
                },
            )

            row = {
                "account": invoice.debit_to,
                "party_type": "Customer",
                "party": invoice.customer,
                "credit_in_account_currency": amount,
            }

        # Invoice Overpayment creates customer credit.
        # Do NOT link the Journal Entry back to the invoice.

        journal.append("accounts", row)

        return journal
