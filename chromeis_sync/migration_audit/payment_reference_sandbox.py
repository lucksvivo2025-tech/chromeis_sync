import frappe


PAYMENT_ENTRY = "ACC-PAY-2026-09607"


def execute():

    print("=" * 80)
    print("PAYMENT ENTRY SANDBOX TEST")
    print("=" * 80)

    try:
        frappe.db.begin()

        pe = frappe.get_doc("Payment Entry", PAYMENT_ENTRY)

        print("\nBefore")
        print("-" * 80)
        print("Payment Entry :", pe.name)
        print("Party         :", pe.party)
        print("Paid Amount   :", pe.paid_amount)
        print("Unallocated   :", pe.unallocated_amount)
        print("References    :", len(pe.references))

        whmcs = frappe.db.sql("""
            SELECT
                ta.invoiceid,
                ta.amountin
            FROM whmcs_mirror.tblaccounts ta
            WHERE ta.id = %s
        """, pe.custom_whmcs_txn_id, as_dict=True)[0]

        invoice = frappe.db.get_value(
            "Sales Invoice",
            {"whmcs_invoice_id": str(whmcs.invoiceid)},
            ["name", "outstanding_amount", "grand_total"],
            as_dict=True,
        )

        print("\nInvoice")
        print("-" * 80)
        print(invoice)

        pe.append(
            "references",
            {
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice.name,
                "allocated_amount": pe.paid_amount,
            },
        )

        print("\nAfter Append")
        print("-" * 80)
        print("References :", len(pe.references))

        pe.save()

        print("\nAfter Save")
        print("-" * 80)

        pe.reload()

        print("Unallocated :", pe.unallocated_amount)
        print("References  :", len(pe.references))

        invoice = frappe.get_doc("Sales Invoice", invoice.name)

        print("Invoice Outstanding :", invoice.outstanding_amount)

        frappe.db.rollback()

        print("\nRollback complete.")

    except Exception:
        frappe.db.rollback()
        raise
