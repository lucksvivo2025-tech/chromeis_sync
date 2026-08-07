from chromeis_sync.sync_engine.framework.builders.base import (
    BaseBuilder,
)


class CustomerBuilder(BaseBuilder):
    """
    Builds an ERPNext Customer payload
    from a WHMCS tblclients row.
    """

    def build(self):

        row = self.source

        return {
            "doctype": "Customer",
            "data": {
                "customer_name": (
                    row.get("companyname")
                    or f"{row.get('firstname', '')} {row.get('lastname', '')}".strip()
                ),
                "customer_group": "Commercial",
                "territory": "All Territories",
                "custom_whmcs_user_id": row["id"],
                "email_id": row.get("email"),
                "mobile_no": row.get("phonenumber"),
            },
        }
