import frappe


class InvoiceBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        invoice = frappe.new_doc("Sales Invoice")

        customer = self.snapshot["customer"]

        customer_name = (
            customer.get("companyname")
            or (
                f"{customer.get('firstname', '')} "
                f"{customer.get('lastname', '')}"
            ).strip()
            or customer.get("email")
            or f"WHMCS Customer {self.snapshot['userid']}"
        )

        invoice.customer = customer_name
        invoice.customer_name = customer_name

        invoice.company = "Chromeis Pvt Ltd"

        invoice.posting_date = self.snapshot["date"]

        if self.snapshot["duedate"] >= self.snapshot["date"]:
            invoice.due_date = self.snapshot["duedate"]
        else:
            invoice.due_date = self.snapshot["date"]

        invoice.currency = "USD"
        invoice.conversion_rate = 1.0
        invoice.selling_price_list = "Standard Selling"
        invoice.price_list_currency = "USD"
        invoice.plc_conversion_rate = 1.0

        invoice.whmcs_invoice_id = str(self.snapshot["id"])
        invoice.custom_whmcs_client_id = str(self.snapshot["userid"])

        invoice.ignore_default_payment_terms_template = 1
        invoice.tax_category = ""

        for row in self.snapshot["items"]:

            amount = float(row.get("amount") or 0)

            description = (row.get("description") or "").strip()

            invoice.append(
                "items",
                {
                    "item_code": "Customer Deposit",
                    "item_name": description[:140] if description else "Customer Deposit",
                    "description": description,
                    "qty": 1,
                    "rate": amount,
                    "amount": amount,
                },
            )

        invoice.set_missing_values()

        for item in invoice.items:
            item.income_account = "Customer Deposits - CPL"
            item.expense_account = None

        invoice.calculate_taxes_and_totals()

        return invoice

