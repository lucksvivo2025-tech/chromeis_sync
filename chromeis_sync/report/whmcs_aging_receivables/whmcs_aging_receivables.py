import frappe
from frappe.utils import today

def execute(filters=None):
    # 1. Define explicit layout columns matching standard accounting formats
    columns = [
        {
            "fieldname": "customer",
            "label": "Client / Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
        {
            "fieldname": "current_due",
            "label": "Current (0 - 30 Days)",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 150
        },
        {
            "fieldname": "period_31_60",
            "label": "31 - 60 Days Overdue",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 160
        },
        {
            "fieldname": "period_61_90",
            "label": "61 - 90 Days Overdue",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 160
        },
        {
            "fieldname": "period_91_above",
            "label": "90+ Days Overdue",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 160
        },
        {
            "fieldname": "total_outstanding",
            "label": "Total Revenue Volume",
            "fieldtype": "Currency",
            "options": "Company:Currency",
            "width": 170
        }
    ]

    current_date = today()

    # 2. Query all submitted invoices regardless of active outstanding balances
    data = frappe.db.sql("""
        SELECT 
            parent.customer as customer,
            SUM(CASE WHEN DATEDIFF(parent.due_date, parent.posting_date) <= 30 THEN parent.grand_total ELSE 0 END) as current_due,
            SUM(CASE WHEN DATEDIFF(parent.due_date, parent.posting_date) BETWEEN 31 AND 60 THEN parent.grand_total ELSE 0 END) as period_31_60,
            SUM(CASE WHEN DATEDIFF(parent.due_date, parent.posting_date) BETWEEN 61 AND 90 THEN parent.grand_total ELSE 0 END) as period_61_90,
            SUM(CASE WHEN DATEDIFF(parent.due_date, parent.posting_date) > 90 THEN parent.grand_total ELSE 0 END) as period_91_above,
            SUM(parent.grand_total) as total_outstanding
        FROM `tabSales Invoice` parent
        WHERE parent.docstatus = 1
        GROUP BY parent.customer
        ORDER BY total_outstanding DESC
    """, as_dict=True)

    return columns, data
