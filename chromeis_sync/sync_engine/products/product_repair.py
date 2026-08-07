import frappe


def backfill_group_ids():

    rows = frappe.db.sql("""
        SELECT
            i.name,
            p.gid
        FROM `tabItem` i
        INNER JOIN whmcs_mirror.tblproducts p
            ON p.id = CAST(i.whmcs_product_id AS UNSIGNED)
        WHERE
            i.whmcs_product_id IS NOT NULL
            AND (
                i.custom_whmcs_group_id IS NULL
                OR i.custom_whmcs_group_id = ''
            )
    """, as_dict=True)

    updated = 0

    for row in rows:
        frappe.db.set_value(
            "Item",
            row["name"],
            "custom_whmcs_group_id",
            str(row["gid"])
        )
        updated += 1

    frappe.db.commit()

    print(f"Updated {updated} Items")
