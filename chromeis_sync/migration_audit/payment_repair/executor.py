import frappe
from frappe.utils import flt

from erpnext.accounts.general_ledger import process_debit_credit_difference
from erpnext.accounts.utils import (
    _delete_adv_pl_entries,
    _delete_pl_entries,
    create_payment_ledger_entry,
    update_voucher_outstanding,
)


from .builder import PaymentReferenceBuilder


class PaymentRepairExecutor:

    def preview(self, candidate):

        pe = frappe.get_doc("Payment Entry", candidate.payment_entry)

        if pe.references:
            raise Exception(
                f"{pe.name} already has Payment Entry References."
            )

        si = frappe.get_doc(
            "Sales Invoice",
            candidate.sales_invoice,
        )

        reference = PaymentReferenceBuilder().build(pe, si)

        print()
        print("=" * 80)
        print("PAYMENT REPAIR PREVIEW")
        print("=" * 80)

        print(f"Payment Entry : {pe.name}")
        print(f"Invoice       : {si.name}")
        print()

        print("=" * 80)
        print("REFERENCE")
        print("=" * 80)

        for k, v in reference.items():
            print(f"{k:25} : {v}")

        return reference

    def execute(self, candidate, commit=False):
        pe = frappe.get_doc("Payment Entry", candidate.payment_entry)

        if len(pe.references):
            raise Exception(f"{pe.name} already contains references.")

        row = pe.append("references", {})

        row.reference_doctype = "Sales Invoice"
        row.reference_name = candidate.sales_invoice
        row.total_amount = flt(candidate.paid_amount)
        row.outstanding_amount = flt(candidate.paid_amount)
        row.allocated_amount = flt(candidate.paid_amount)

        pe.flags.ignore_validate_update_after_submit = True

        pe.clear_unallocated_reference_document_rows()
        pe.setup_party_account_field()
        pe.set_missing_values()
        pe.set_missing_ref_details(force=True)
        pe.set_amounts()

        pe.save(ignore_permissions=True)

        # ------------------------------------------------------------------
        # Rebuild Payment Ledger Entries (same flow used by ERPNext
        # reconciliation)
        # ------------------------------------------------------------------

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

        si = frappe.get_doc("Sales Invoice", candidate.sales_invoice)

        update_voucher_outstanding(
           "Sales Invoice",
           candidate.sales_invoice,
           si.debit_to,
           pe.party_type,
           pe.party,
        )

        if commit:
            frappe.db.commit()

        return pe
