import re
import frappe


class CustomerBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def _customer_name(self):
        """
        Build a safe customer name.

        ERP Customer.name is generated from customer_name
        (naming_series:), so keep it well below 140 chars.
        """

        name = (
            self.snapshot.get("companyname")
            or (
                f"{self.snapshot.get('firstname', '')} "
                f"{self.snapshot.get('lastname', '')}"
            ).strip()
            or self.snapshot.get("email")
            or f"WHMCS Customer {self.snapshot['id']}"
        )

        name = " ".join(str(name).split())

        if len(name) > 120:
            name = name[:120]

        return name

    def _phone(self):
        """
        Normalize phone number.

        ERPNext validates phone numbers.
        Invalid values are ignored.
        """

        phone = (self.snapshot.get("phonenumber") or "").strip()

        if ";" in phone:
            phone = phone.split(";")[0].strip()

        if "," in phone:
            phone = phone.split(",")[0].strip()

        phone = re.sub(r"[^0-9+()\- ]", "", phone)

        digits = re.sub(r"\D", "", phone)

        if len(digits) < 6:
            return ""

        if len(phone) > 140:
            phone = phone[:140]

        return phone

    def build(self):

        customer = frappe.new_doc("Customer")

        customer.customer_name = self._customer_name()

        customer.customer_type = "Company"
        customer.customer_group = "Commercial"
        customer.territory = "All Territories"

        # WHMCS IDs
        customer.whmcs_id = str(self.snapshot["id"])
        customer.custom_whmcs_user_id = str(self.snapshot["id"])

        # Email
        customer.email_id = (self.snapshot.get("email") or "")[:140]

        # Phone
        customer.mobile_no = self._phone()

        customer.default_currency = "USD"
        customer.language = "en"

        return customer
