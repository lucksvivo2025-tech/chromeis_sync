import frappe


class MissingInvoiceSnapshot:

    @staticmethod
    def create(whmcs_invoice_id):

        invoices = frappe.db.sql("""
            SELECT *
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
        """, whmcs_invoice_id, as_dict=True)

        if not invoices:
            raise Exception(
                f"WHMCS Invoice {whmcs_invoice_id} not found."
            )

        invoice = invoices[0]

        items = frappe.db.sql("""
            SELECT *
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
        """, whmcs_invoice_id, as_dict=True)

        customer = frappe.db.sql("""
            SELECT
                name,
                customer_name,
                custom_whmcs_client_id,
                default_currency
            FROM `tabCustomer`
            WHERE custom_whmcs_client_id=%s
            LIMIT 1
        """, invoice["userid"], as_dict=True)

        if not customer:
            raise Exception(
                f"Customer WH-CUST-{invoice['userid']} not found."
            )

        customer = customer[0]

        company = "Chromeis Pvt Ltd"

        currency = customer.get("default_currency") or "USD"

        return {
            "header": {
                "whmcs_invoice_id": str(invoice["id"]),
                "customer": customer["name"],
                "customer_name": customer["customer_name"],
                "custom_whmcs_client_id": customer["custom_whmcs_client_id"],
                "company": company,
                "posting_date": invoice["date"],
                "due_date": invoice["date"],
                "currency": currency,
                "remarks": (
                    f"WHMCS ID: {invoice['id']} | "
                    f"Customer Ref: {customer['name']}"
                ),
                "debit_to": "Debtors - CPL",
            },
            "whmcs_invoice": invoice,
            "items": items,
        }
