import frappe

def execute(filters=None):
    # 1. Explicitly define your columns block right here
    columns = [
        {
            "fieldname": "client",
            "label": "Client / Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
        {
            "fieldname": "total_paid",
            "label": "Total Paid Balance",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 150
        },
        {
            "fieldname": "count",
            "label": "Invoice Count",
            "fieldtype": "Int",
            "width": 100
        }
    ]

    # 2. Your database query logic (Ensure fieldnames match lowercase keys above)
    data = frappe.db.sql("""
        SELECT 
            customer as client, 
            SUM(grand_total) as total_paid, 
            COUNT(name) as count 
        FROM `tabSales Invoice` 
        WHERE docstatus = 1 
        GROUP BY customer
    """, as_dict=True)

    # 3. Return BOTH columns and data arrays explicitly
    return columns, data
