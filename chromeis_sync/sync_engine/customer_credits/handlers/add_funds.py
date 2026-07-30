import re
import frappe


class AddFundsHandler:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        invoice_id = self.snapshot.get("relid")

        # Newer WHMCS versions store the invoice number only in the description
        if not invoice_id:
            description = self.snapshot.get("description") or ""

            match = re.search(
                r"Add\s+Funds\s+Invoice\s+#(\d+)",
                description,
                re.IGNORECASE,
            )

            if match:
                invoice_id = match.group(1)

        if not invoice_id:
            raise Exception(
                f"Unable to determine Add Funds invoice for WHMCS Credit {self.snapshot['id']}"
            )

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(invoice_id)
            },
            ["name", "customer", "debit_to"],
            as_dict=True,
        )

        if not invoice:
            raise Exception(
                f"ERP Invoice not found for WHMCS Invoice {invoice_id}"
            )

        journal = frappe.new_doc("Journal Entry")

        journal.voucher_type = "Journal Entry"
        journal.company = "Chromeis Pvt Ltd"
        journal.posting_date = self.snapshot["date"]

        journal.user_remark = (
            self.snapshot.get("description")
            or f"WHMCS Add Funds #{self.snapshot['id']}"
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

        # Attach the invoice reference whenever an invoice has been resolved
        row["reference_type"] = "Sales Invoice"
        row["reference_name"] = invoice.name

        journal.append("accounts", row)

        return journal
