from __future__ import annotations

import frappe


class ERPPaymentProvider:
    """Loads payment information from ERPNext."""

    def load_payment(self, whmcs_txn_id):

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

    def load_references(self, payment_entry):

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
