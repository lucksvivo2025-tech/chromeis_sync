import frappe

from chromeis_sync.migration_audit.infrastructure.whmcs import WHMCSDatabase


class PaymentAllocationValidator:

    def load_whmcs_payments(self):

        return WHMCSDatabase.query("""
            SELECT
                id,
                userid,
                invoiceid,
                amountin,
                description,
                date
            FROM tblaccounts
            WHERE description = 'Invoice Payment'
            ORDER BY id
        """)

    def find_erp_payment(self, whmcs_txn_id):

        return frappe.db.get_value(
            "Payment Entry",
            {
                "custom_whmcs_txn_id": str(whmcs_txn_id)
            },
            [
                "name",
                "party",
                "paid_amount",
                "unallocated_amount"
            ],
            as_dict=True,
        )

    def load_payment_references(self, payment_entry):

        return frappe.db.get_all(
            "Payment Entry Reference",
            filters={
                "parent": payment_entry,
            },
            fields=[
                "reference_doctype",
                "reference_name",
                "allocated_amount",
            ],
        )
    def validate_payment(self, payment):

        result = {
            "whmcs_txn_id": payment["id"],
            "invoice_id": payment["invoiceid"],
            "amount": payment["amountin"],
            "status": "PASS",
            "reason": None,
        }

        erp_payment = self.find_erp_payment(payment["id"])

        if not erp_payment:
            result["status"] = "FAIL"
            result["reason"] = "Missing ERP Payment"
            return result

        references = self.load_payment_references(erp_payment["name"])

        if payment["invoiceid"] and not references:
            result["status"] = "FAIL"
            result["reason"] = "Missing Allocation"

        return result

    def run(self):

        payments = self.load_whmcs_payments()

        results = []

        for payment in payments:
            results.append(
                self.validate_payment(payment)
            )

        return results
