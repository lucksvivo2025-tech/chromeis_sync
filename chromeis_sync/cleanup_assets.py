import frappe

def scrap_cloud_assets():
    # Find all Draft Cloud assets
    assets = frappe.get_all("Asset", filters={
        "item_name": ["like", "%Cloud/VPS%"],
        "status": "Draft"
    }, fields=["name"])
    
    print(f"Found {len(assets)} draft Cloud/VPS assets. Scrapping...")
    
    for a in assets:
        # Direct database update ignores broken links (like missing Custodian)
        frappe.db.set_value("Asset", a.name, "status", "Scrapped")
        print(f"Scrapped {a.name}")
    
    frappe.db.commit()
    print("Cleanup complete.")
