import frappe


class HostingRecoveryAnalyzer:

    @staticmethod
    def analyze(service_id):

        service = frappe.db.sql(
            """
            SELECT
                h.id,
                h.userid,
                h.packageid,
                h.server,
                h.domain,
                p.name AS product_name,
                p.gid AS product_group
            FROM whmcs_mirror.tblhosting h
            LEFT JOIN whmcs_mirror.tblproducts p
                   ON p.id = h.packageid
            WHERE h.id=%s
            """,
            (service_id,),
            as_dict=True,
        )

        if not service:
            return {
                "found": False,
                "reason": "WHMCS Service not found",
            }

        service = service[0]

        subscription = frappe.get_all(
            "Subscription",
            filters={
                "whmcs_service_id": str(service_id),
            },
            fields=[
                "name",
                "party",
                "status",
            ],
            limit_page_length=1,
        )

        return {
            "found": True,
            "service": service,
            "subscription": subscription[0] if subscription else None,
        }
