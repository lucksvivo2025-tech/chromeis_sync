import frappe


class ServiceBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def build(self):

        service = frappe.new_doc("WHMCS Service")

        service.whmcs_service_id = str(self.snapshot["id"])
        service.whmcs_user_id = str(self.snapshot["userid"])

        service.domain = self.snapshot.get("domain")

        service.product_name = (
            self.snapshot.get("product", {}).get("name")
            or "Unknown Product"
        )

        service.status = self.snapshot.get("domainstatus")

        service.billing_cycle = self.snapshot.get("billingcycle")

        service.next_due_date = self.snapshot.get("nextduedate")

        service.amount = self.snapshot.get("amount") or 0

        service.username = self.snapshot.get("username")

        service.dedicated_ip = self.snapshot.get("dedicatedip")

        service.customer_name = (
            self.snapshot.get("client", {}).get("companyname")
            or (
                f"{self.snapshot.get('client', {}).get('firstname', '')} "
                f"{self.snapshot.get('client', {}).get('lastname', '')}"
            ).strip()
        )

        return service
