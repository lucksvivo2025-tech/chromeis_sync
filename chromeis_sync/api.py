import frappe
from frappe.utils import flt

def get_customer_intelligence_dashboard(doc, method=None):
    """
    Calculates live customer operational metrics, falling back gracefully
    if the customer record string varies between WHMCS tracking systems.
    """
    if not doc.name:
        return

    # Fallback checks: try matching against both the ID name and the linked customer naming representations
    customer_target = doc.name
    customer_title = doc.customer_name if hasattr(doc, 'customer_name') else doc.name

    # 1. Gross Revenue (Paid Invoices)
    paid_data = frappe.db.sql("""
        SELECT COUNT(name) as count, SUM(grand_total) as total 
        FROM `tabSales Invoice` 
        WHERE (status = 'Paid' OR outstanding_amount = 0) 
        AND (customer = %s OR customer = %s)
    """, (customer_target, customer_title), as_dict=True)[0]
    
    # 2. Current Live Outstanding Balance (Unpaid or Overdue Invoices)
    unpaid_data = frappe.db.sql("""
        SELECT COUNT(name) as count, SUM(outstanding_amount) as total 
        FROM `tabSales Invoice` 
        WHERE outstanding_amount > 0 
        AND (customer = %s OR customer = %s)
    """, (customer_target, customer_title), as_dict=True)[0]

    # 3. Upstream Infrastructure Vendor Costs linked to this specific client (Fixed Column Definition)
    cost_data = frappe.db.sql("""
        SELECT SUM(base_amount) as total 
        FROM `tabPurchase Invoice Item` 
        WHERE docstatus = 1 
        AND rented_to_customer = %s
    """, (customer_target,), as_dict=True)[0].total or 0.0

    # 4. Fetch Active Service Line Items
    items_data = frappe.db.sql("""
        SELECT DISTINCT sii.item_name, sii.description
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE (si.customer = %s OR si.customer = %s)
        ORDER BY si.creation DESC
    """, (customer_target, customer_title), as_dict=True)

    services = []
    assets = []
    
    for i in items_data:
        if i.item_name and i.item_name not in services:
            services.append(i.item_name)
        if i.description and i.description not in assets:
            clean_desc = " ".join(i.description.splitlines()).strip()
            if len(clean_desc) > 50:
                clean_desc = clean_desc[:47] + "..."
            assets.append(clean_desc)

    # Bind values back cleanly onto the frontend payload object
    doc.set_onload('val_paid_count', paid_data.count or 0)
    doc.set_onload('val_paid', flt(paid_data.total or 0.0))
    doc.set_onload('val_unpaid_count', unpaid_data.count or 0)
    doc.set_onload('val_unpaid', flt(unpaid_data.total or 0.0))
    doc.set_onload('val_cost', flt(cost_data))
    doc.set_onload('val_services_count', len(services))
    doc.set_onload('val_services_list', ", ".join(services[:3]) if services else "Hosting Allocation")
    doc.set_onload('val_assets_list', ", ".join(assets[:2]) if assets else "Core Network Block")
