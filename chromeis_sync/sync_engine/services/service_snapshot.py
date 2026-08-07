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


        # -------------------------
        # CLIENT LOOKUP
        # -------------------------

        client_deleted = False

        client = frappe.db.sql(
            """
            SELECT
                id,
                firstname,
                lastname,
                companyname,
                email
            FROM whmcs_mirror.tblclients
            WHERE id=%s
            """,
            (service.userid,),
            as_dict=True,
        )


        if client:

            client = client[0]

        else:

            client_deleted = True

            client = {
                "id": service.userid,
                "firstname": "Deleted",
                "lastname": f"WHMCS Client {service.userid}",
                "companyname": "",
                "email": "",
            }



        # -------------------------
        # PRODUCT LOOKUP
        # -------------------------

        product_deleted = False

        product = frappe.db.sql(
            """
            SELECT
                id,
                name
            FROM whmcs_mirror.tblproducts
            WHERE id=%s
            """,
            (service.packageid,),
            as_dict=True,
        )


        if product:

            product = product[0]

        else:

            product_deleted = True

            product = {
                "id": service.packageid,
                "name": f"Deleted WHMCS Product {service.packageid}",
            }



        # -------------------------
        # FINAL SNAPSHOT
        # -------------------------

        return {

            "id": service.id,

            "userid": service.userid,

            "packageid": service.packageid,

            "domain": service.domain,

            "paymentmethod": service.paymentmethod,

            "qty": service.qty,

            "amount": service.amount,

            "billingcycle": service.billingcycle,

            "nextduedate": service.nextduedate,

            "domainstatus": service.domainstatus,

            "username": service.username,

            "dedicatedip": service.dedicatedip,


            "client": client,

            "product": product,


            # flags
            "client_deleted": client_deleted,

            "product_deleted": product_deleted,
        }
