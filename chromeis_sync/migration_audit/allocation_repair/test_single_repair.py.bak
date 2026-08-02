import frappe

from chromeis_sync.migration_audit.payment_repair.builder import (
    PaymentReferenceBuilder,
)

PAYMENT_ENTRY = "ACC-PAY-2026-09607"

# False = Test only (ROLLBACK)
# True  = Actually repair ONE Payment Entry
COMMIT = True


def run():

    print("=" * 80)
    print("TEST SINGLE PAYMENT REPAIR")
    print("=" * 80)

    pe = frappe.get_doc("Payment Entry", PAYMENT_ENTRY)

    print(f"Payment Entry      : {pe.name}")
    print(f"Current References : {len(pe.references)}")
    print(f"Paid Amount        : {pe.paid_amount}")
    print(f"Unallocated        : {pe.unallocated_amount}")
    print()

    if pe.references:
        raise Exception("Payment Entry already contains references.")

    if not pe.custom_whmcs_txn_id:
        raise Exception("Missing WHMCS Transaction ID.")

    invoice = frappe.db.sql(
        """
        SELECT
            si.name
        FROM whmcs_mirror.tblaccounts a
        INNER JOIN `tabSales Invoice` si
            ON si.whmcs_invoice_id = a.invoiceid
        WHERE a.id = %s
        LIMIT 1
        """,
        (pe.custom_whmcs_txn_id,),
        as_dict=True,
    )

    if not invoice:
        raise Exception("Unable to locate Sales Invoice.")

    si = frappe.get_doc("Sales Invoice", invoice[0]["name"])

    reference = PaymentReferenceBuilder().build(pe, si)

    print("Appending reference...")
    pe.append("references", reference)

    print("Refreshing ERPNext reference details...")
    pe.set_missing_ref_details(force=True)

    print("Recalculating allocations...")
    pe.set_total_allocated_amount()
    pe.set_unallocated_amount()

    print()
    print("=" * 80)
    print("AFTER RECALCULATION")
    print("=" * 80)

    print("Reference Count :", len(pe.references))
    print("Allocated Total :", pe.total_allocated_amount)
    print("Unallocated     :", pe.unallocated_amount)

    print()
    print("REFERENCE VALUES")
    print("-" * 80)

    for r in pe.references:
        print(
            {
                "reference_doctype": r.reference_doctype,
                "reference_name": r.reference_name,
                "total_amount": r.total_amount,
                "outstanding_amount": r.outstanding_amount,
                "allocated_amount": r.allocated_amount,
                "account": r.account,
                "exchange_rate": r.exchange_rate,
            }
        )

    if not COMMIT:

        print()
        print("=" * 80)
        print("ROLLBACK")
        print("=" * 80)

        frappe.db.rollback()

        print("Rollback complete.")
        return

    print()
    print("=" * 80)
    print("COMMIT MODE")
    print("=" * 80)

    #
    # Prevent accounting repost during this repair
    #
    pe.flags.ignore_reposting_on_reconciliation = True

    #
    # Save the submitted Payment Entry
    #
    pe.save()

    print("Save successful.")

    #
    # Verify before commit
    #
    print()
    print("VERIFY BEFORE COMMIT")
    print("-" * 80)
    print("Reference Count :", len(pe.references))
    print("Allocated Total :", pe.total_allocated_amount)
    print("Unallocated     :", pe.unallocated_amount)

    frappe.db.commit()

    print()
    print("Database committed.")

    #
    # Reload from database
    #
    pe = frappe.get_doc("Payment Entry", PAYMENT_ENTRY)

    print()
    print("=" * 80)
    print("VERIFICATION AFTER COMMIT")
    print("=" * 80)

    print("Reference Count :", len(pe.references))
    print("Allocated Total :", pe.total_allocated_amount)
    print("Unallocated     :", pe.unallocated_amount)

    print()

    for r in pe.references:
        print(
            {
                "reference_doctype": r.reference_doctype,
                "reference_name": r.reference_name,
                "allocated_amount": r.allocated_amount,
                "account": r.account,
            }
        )

    print()
    print("=" * 80)
    print("SUCCESS")
    print("=" * 80)
