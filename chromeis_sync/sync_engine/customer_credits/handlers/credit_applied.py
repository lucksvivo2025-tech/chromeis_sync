import frappe


class CreditAppliedHandler:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {
                "whmcs_invoice_id": str(self.snapshot["relid"])
            },
            ["name", "customer", "debit_to", "docstatus"],
            as_dict=True,
        )

        if not invoice:
            raise Exception(
                f"ERP Invoice not found for WHMCS Invoice {self.snapshot['relid']}"
            )

        if invoice.docstatus == 2:
            raise Exception(
                f"ERP Invoice {invoice.name} is cancelled"
            )

        amount = abs(float(self.snapshot.get("amount") or 0))

        if amount == 0:
            return None

        journal = frappe.new_doc("Journal Entry")

        journal.company = "Chromeis Pvt Ltd"
        journal.posting_date = self.snapshot["date"]
        journal.voucher_type = "Journal Entry"

        journal.user_remark = (
            self.snapshot.get("description")
            or f"WHMCS Credit Applied #{self.snapshot['id']}"
        )

        journal.custom_whmcs_credit_id = str(self.snapshot["id"])

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

        erp_invoice = frappe.get_doc("Sales Invoice", invoice.name)

        if (
            erp_invoice.docstatus == 1
            and erp_invoice.status != "Cancelled"
            and erp_invoice.outstanding_amount >= amount
        ):
            row["reference_type"] = "Sales Invoice"
            row["reference_name"] = invoice.name

        journal.append("accounts", row)

        return journal
