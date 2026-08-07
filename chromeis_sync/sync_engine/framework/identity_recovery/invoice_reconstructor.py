from chromeis_sync.sync_engine.framework.classification.business_mapper import (
    BusinessMapper,
)


class InvoiceReconstructor:

    @staticmethod
    def reconstruct(snapshot):

        rows = []

        for item in snapshot.items:

            whmcs_item = {
                "type": item.item_code,
                "relid": (
                    item.custom_whmcs_service_id
                    or item.custom_whmcs_domain_id
                    or item.custom_whmcs_addon_id
                    or 0
                ),
                "description": item.description,
                "amount": float(item.amount),
            }

            mapping = BusinessMapper.map(
                whmcs_item
            )

            if not mapping:
                continue

            rows.append(
                {
                    "family": mapping["family"],
                    "name": mapping.get("name"),
                    "item_code": mapping["item_code"],
                    "item_name": mapping["item_name"],
                    "description": mapping["description"],
                    "qty": mapping["qty"],
                    "rate": mapping["rate"],
                    "amount": mapping["amount"],
                    "income_account": mapping["income_account"],
                    "type": whmcs_item["type"],
                    "relid": whmcs_item["relid"],
                }
            )

        return {

            "invoice": snapshot.header.whmcs_invoice_id,

            "customer": snapshot.header.custom_whmcs_client_id,

            "rows": rows,

            "row_count": len(rows),

            "total": round(
                sum(
                    row["amount"]
                    for row in rows
                ),
                2,
            ),

        }
