import frappe

def audit_custodians():
    # Fetch only Submitted (Active) Assets
    assets = frappe.get_all("Asset", filters={"status": "Submitted"}, 
                            fields=["name", "item_name", "custodian", "asset_owner"])
    
    print(f"\n--- Active Asset Custodians ---\n")
    for a in assets:
        # Retrieve the employee name if assigned
        custodian = a.custodian or "Not Assigned"
        print(f"Asset: {a.item_name[:20]}... | Custodian: {custodian}")

if __name__ == "__main__":
    audit_custodians()
