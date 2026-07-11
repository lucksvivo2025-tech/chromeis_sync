import frappe

def execute(filters=None):
    # 1. Define UI Columns explicitly
    columns = [
        {
            "fieldname": "month",
            "label": "Billing Month",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "monthly_revenue",
            "label": "Total Income Collected",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 180
        },
        {
            "fieldname": "invoice_count",
            "label": "Invoices Processed",
            "fieldtype": "Int",
            "width": 120
        }
    ]

    # 2. SQL to pull submitted data grouped by Year-Month formatting
    data = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(posting_date, '%Y-%m') as month,
            SUM(grand_total) as monthly_revenue,
            COUNT(name) as invoice_count
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        GROUP BY DATE_FORMAT(posting_date, '%Y-%m')
        ORDER BY month DESC
    """, as_dict=True)

    return columns, data
