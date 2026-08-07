import frappe


class CustomerBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot


    def build(self):

        customer = frappe.new_doc("Customer")

        firstname = self.snapshot.get("firstname") or ""
        lastname = self.snapshot.get("lastname") or ""
        companyname = self.snapshot.get("companyname") or ""

        # Customer Name priority
        if companyname and companyname.strip() and companyname.strip() != "N/A":
            customer.customer_name = companyname.strip()
        else:
            customer.customer_name = (
                firstname.strip() + " " + lastname.strip()
            ).strip()


        # WHMCS mapping
        customer.whmcs_id = str(self.snapshot.get("id"))

        customer.custom_whmcs_user_id = str(
            self.snapshot.get("id")
        )


        # Customer type
        if companyname and companyname.strip() and companyname.strip() != "N/A":
            customer.customer_type = "Company"
        else:
            customer.customer_type = "Individual"


        # Basic fields
        customer.customer_group = "Commercial"
        customer.territory = "All Territories"

        if self.snapshot.get("email"):
            customer.email_id = self.snapshot.get("email")

        if self.snapshot.get("phonenumber"):
            customer.mobile_no = self.snapshot.get("phonenumber")


        return customer
