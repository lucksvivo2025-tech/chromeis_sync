import frappe

def execute(filters=None):
    # 1. Setup UI Layout columns for product analytics tracking
    columns = [
        {
            "fieldname": "item_code",
            "label": "Product / Plan Code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180
        },
        {
            "fieldname": "item_name",
            "label": "Plan Description",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "fieldname": "total_qty",
            "label": "Active Subscriptions sold",
            "fieldtype": "Float",
            "width": 160
        },
        {
            "fieldname": "avg_rate",
            "label": "Average Unit Pricing",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 150
        },
        {
            "fieldname": "total_amount",
            "label": "Gross Revenue Margin",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 180
        }
    ]

    # 2. Join Sales Invoice with its Sales Invoice Item child table
    data = frappe.db.sql("""
        SELECT 
            child.item_code as item_code,
            child.item_name as item_name,
            SUM(child.qty) as total_qty,
            AVG(child.rate) as avg_rate,
            SUM(child.amount) as total_amount
        FROM `tabSales Invoice` parent
        INNER JOIN `tabSales Invoice Item` child ON child.parent = parent.name
        WHERE parent.docstatus = 1
        GROUP BY child.item_code, child.item_name
        ORDER BY total_amount DESC
    """, as_dict=True)

    return columns, data
