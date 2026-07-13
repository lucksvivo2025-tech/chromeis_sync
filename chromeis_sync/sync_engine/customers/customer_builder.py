import frappe


class CustomerBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        customer = frappe.new_doc("Customer")

        customer.customer_name = (
            self.snapshot.get("companyname")
            or f"{self.snapshot.get('firstname', '')} {self.snapshot.get('lastname', '')}".strip()
            or self.snapshot.get("email")
            or f"WHMCS Customer {self.snapshot['id']}"
        )

        customer.customer_type = "Company"
        customer.customer_group = "Commercial"
        customer.territory = "All Territories"

        # WHMCS IDs
        customer.whmcs_id = str(self.snapshot["id"])
        customer.custom_whmcs_user_id = str(self.snapshot["id"])

        # Email
        customer.email_id = self.snapshot.get("email")

        # Phone normalization
        phone = (self.snapshot.get("phonenumber") or "").strip()

        if ";" in phone:
            phone = phone.split(";")[0].strip()

        if "," in phone:
            phone = phone.split(",")[0].strip()

        customer.mobile_no = phone

        # Defaults
        customer.default_currency = "USD"
        customer.language = "en"

        return customer
