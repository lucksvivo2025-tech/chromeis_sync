from chromeis_sync.migration_audit.infrastructure.whmcs import WHMCSDatabase
import frappe


class CustomerCreditValidator:

    def run(self):

        print("=" * 80)
        print("CUSTOMER CREDIT RECONCILIATION")
        print("=" * 80)

        customers = WHMCSDatabase.query("""
            SELECT
                id,
                credit
            FROM tblclients
            WHERE credit > 0
            ORDER BY credit DESC
        """)

        stats = {
            "MATCHED": 0,
            "CONSUMED_BY_INVOICE": 0,
            "MISSING": 0,
        }

        for customer in customers:

            result = self.validate_customer(customer)

            stats[result["status"]] += 1

            print(
                f"{result['party']:15} "
                f"WHMCS={result['whmcs_credit']:10.2f} "
                f"ERP_CREDIT={result['erp_credit']:10.2f} "
                f"ERP_ALLOCATED={result['erp_allocated']:10.2f} "
                f"{result['status']}"
            )

        print("=" * 80)
        print(stats)


    def validate_customer(self, customer):

        party = f"WH-CUST-{customer['id']}"

        whmcs_credit = float(customer["credit"])


        # Current ERP customer credit balance
        gl = frappe.db.sql("""
            SELECT
                COALESCE(SUM(credit),0)
                -
                COALESCE(SUM(debit),0)
                AS balance
            FROM `tabGL Entry`

            WHERE party=%s
            AND party_type='Customer'
            AND account LIKE 'Debtors%%'
            AND is_cancelled = 0

        """, party, as_dict=True)[0]


        erp_credit = float(gl.balance or 0)


        # Payment allocations against invoices
        allocated = frappe.db.sql("""
            SELECT
                COALESCE(SUM(per.allocated_amount),0)
                AS allocated
            FROM `tabPayment Entry Reference` per
            INNER JOIN `tabPayment Entry` pe
                ON pe.name = per.parent
            WHERE pe.party=%s
            AND pe.docstatus=1
        """, party, as_dict=True)[0]


        erp_allocated = float(
            allocated.allocated or 0
        )


        # Classification

        if abs(erp_credit - whmcs_credit) < 0.01:

            status = "MATCHED"

        elif erp_allocated >= whmcs_credit:

            status = "CONSUMED_BY_INVOICE"

        else:

            status = "MISSING"


        return {
            "party": party,
            "whmcs_credit": whmcs_credit,
            "erp_credit": erp_credit,
            "erp_allocated": erp_allocated,
            "status": status,
        }
