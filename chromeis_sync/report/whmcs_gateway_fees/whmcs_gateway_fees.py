import frappe

def execute(filters=None):
    # 1. Setup UI Layout columns for financial matching
    columns = [
        {
            "fieldname": "gateway",
            "label": "Payment Gateway / Method",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "fieldname": "gross_received",
            "label": "Gross Income",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 160
        },
        {
            "fieldname": "estimated_fees",
            "label": "Gateway Fees (Est. 3%)",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 160
        },
        {
            "fieldname": "net_income",
            "label": "Net Revenue",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 160
        }
    ]

    # 2. Left Join ensures all invoices display even if child rows aren't written yet
    data = frappe.db.sql("""
        SELECT 
            COALESCE(NULLIF(child.mode_of_payment, ''), 'Direct Sync / Paid') as gateway,
            SUM(parent.grand_total) as gross_received,
            SUM(parent.grand_total * 0.03) as estimated_fees,
            SUM(parent.grand_total - (parent.grand_total * 0.03)) as net_income
        FROM `tabSales Invoice` parent
        LEFT JOIN `tabSales Invoice Payment` child ON child.parent = parent.name
        WHERE parent.docstatus = 1
        GROUP BY COALESCE(NULLIF(child.mode_of_payment, ''), 'Direct Sync / Paid')
    """, as_dict=True)

    return columns, data
