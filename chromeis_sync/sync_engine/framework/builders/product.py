from chromeis_sync.sync_engine.framework.builders.base import (
    BaseBuilder,
)


class ProductBuilder(BaseBuilder):
    """
    Builds an ERPNext Item payload
    from a WHMCS tblproducts row.
    """

    def build(self):

        row = self.source

        return {
            "doctype": "Item",
            "data": {
                "item_code": str(row["id"]),
                "item_name": row["name"],
                "item_group": "Services",
                "stock_uom": "Nos",
                "is_stock_item": 0,
                "custom_whmcs_product_id": row["id"],
            },
        }
