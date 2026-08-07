from chromeis_sync.sync_engine.framework.builders.base import (
    BaseBuilder,
)

from chromeis_sync.sync_engine.framework.identity.service import (
    IdentityService,
)


class OrderBuilder(BaseBuilder):
    """
    Builds an ERPNext Sales Order payload
    from a WHMCS tblorders row.
    """

    def build(self):

        row = self.source

        customer = IdentityService.resolve_customer(
            user_id=row["userid"],
        )

        return {
            "doctype": "Sales Order",
            "data": {
                "customer": customer.document_name,
                "transaction_date": row["date"].date(),
                "delivery_date": row["date"].date(),
                "custom_whmcs_order_id": row["id"],
            },
        }
