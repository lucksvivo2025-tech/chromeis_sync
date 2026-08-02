import frappe
from frappe.utils import flt

from erpnext.accounts.general_ledger import process_debit_credit_difference
from erpnext.accounts.utils import (
    _delete_adv_pl_entries,
    _delete_pl_entries,
    create_payment_ledger_entry,
    update_voucher_outstanding,
)


class PaymentRepairExecutor:

    def preview(self, candidate):

        print()
        print("=" * 80)
        print("ALLOCATION REPAIR PREVIEW")
        print("=" * 80)

        print(f"Payment Entry      : {candidate.payment_entry}")
        print(f"Payment Reference  : {candidate.payment_reference}")
        print(f"Sales Invoice      : {candidate.sales_invoice}")
        print()

        print(f"Paid Amount        : {candidate.paid_amount}")
        print(f"Invoice Total      : {candidate.grand_total}")
        print(f"Current Allocated  : {candidate.allocated_amount}")

        repaired = min(
            float(candidate.paid_amount),
            float(candidate.grand_total),
        )

        print(f"New Allocated      : {repaired}")

    def execute(self, candidate, commit=False):

        pe = frappe.get_doc(
            "Payment Entry",
            candidate.payment_entry,
        )

        ref = None

        for r in pe.references:
            if r.name == candidate.payment_reference:
                ref = r
                break

        if not ref:
            raise Exception(
                f"Reference {candidate.payment_reference} not found."
            )

        repaired = min(
            float(pe.paid_amount),
            float(candidate.grand_total),
        )

        ref.total_amount = flt(candidate.grand_total)
        ref.outstanding_amount = flt(candidate.reference_outstanding)
        ref.allocated_amount = flt(repaired)

        pe.flags.ignore_validate_update_after_submit = True

        # Recalculate payment totals after changing allocation
        pe.set_total_allocated_amount()
        pe.set_unallocated_amount()
        pe.set_difference_amount()

        pe.save(ignore_permissions=True)

        # ------------------------------------------------------------
        # Rebuild Payment Ledger Entries
        # ------------------------------------------------------------

        _delete_pl_entries(pe.doctype, pe.name)
        _delete_adv_pl_entries(pe.doctype, pe.name)

        gl_map = pe.build_gl_map()

        process_debit_credit_difference(gl_map)

        create_payment_ledger_entry(
            gl_map,
            update_outstanding="No",
            cancel=0,
            adv_adj=1,
        )

        si = frappe.get_doc(
            "Sales Invoice",
            candidate.sales_invoice,
        )

        update_voucher_outstanding(
            "Sales Invoice",
            si.name,
            si.debit_to,
            pe.party_type,
            pe.party,
        )

        if commit:
            frappe.db.commit()

        return pe
