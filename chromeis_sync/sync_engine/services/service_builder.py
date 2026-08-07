import frappe


class ServiceBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot


    def build(self):

        service = frappe.new_doc("WHMCS Service")

        service.name = f"WHMCS-SERVICE-{self.snapshot['id']}"

        service.whmcs_service_id = self.snapshot["id"]

        service.whmcs_user_id = self.snapshot["userid"]


        client = self.snapshot["client"]

        service.customer_name = (
            client.get("companyname")
            or f"{client.get('firstname','')} {client.get('lastname','')}"
        )


        product = self.snapshot["product"]

        service.product_name = product.get("name")


        service.domain = self.snapshot.get("domain")

        service.status = self.snapshot.get("domainstatus")

        service.billing_cycle = self.snapshot.get("billingcycle")

        service.next_due_date = self.snapshot.get("nextduedate")

        service.amount = self.snapshot.get("amount")

        service.username = self.snapshot.get("username")

        service.dedicated_ip = self.snapshot.get("dedicatedip")


        # Deleted flags

        service.client_deleted = (
            1 if self.snapshot.get("client_deleted") else 0
        )

        service.product_deleted = (
            1 if self.snapshot.get("product_deleted") else 0
        )


        return service
