import frappe

def audit_assets():
    # Use the ORM exclusively, no raw SQL
    assets = frappe.get_all("Asset", fields=["name", "item_name", "status", "customer"])

    print(f"\n--- Total Assets Found: {len(assets)} ---\n")

    for a in assets:
        doc = frappe.get_doc("Asset", a.name)
        # Safe access to serial number
        serial = doc.get("serial_no") or "N/A"
        print(f"Item: {a.item_name[:20]}... | Status: {a.status} | Serial: {serial} | Assigned: {a.customer}")
