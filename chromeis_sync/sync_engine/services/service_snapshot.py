import frappe


class ServiceSnapshot:

    @staticmethod
    def create(service_id):

        service = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblhosting
            WHERE id=%s
            """,
            (service_id,),
            as_dict=True,
        )

        if not service:
            raise Exception(f"WHMCS Service {service_id} not found")

        service = service[0]

        client = frappe.db.sql(
            """
            SELECT
                firstname,
                lastname,
                companyname,
                email
            FROM whmcs_mirror.tblclients
            WHERE id=%s
            """,
            (service["userid"],),
            as_dict=True,
        )

        service["client"] = client[0] if client else {}

        product = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblproducts
            WHERE id=%s
            """,
            (service["packageid"],),
            as_dict=True,
        )

        service["product"] = product[0] if product else {}

        return service
