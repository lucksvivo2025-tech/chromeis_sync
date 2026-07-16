import frappe


class CustomerCreditValidator:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def validate(self):

        amount = float(self.snapshot.get("amount") or 0)

        # ---------------------------------------------------
        # Zero-value credits don't produce accounting entries.
        # ---------------------------------------------------
        if amount == 0:
            return False, "SKIP_ZERO_AMOUNT"

        relid = int(self.snapshot.get("relid") or 0)

        # ---------------------------------------------------
        # Credits without invoice reference (wallet/add funds)
        # ---------------------------------------------------
        if relid == 0:
            return True, None

        # ---------------------------------------------------
        # Verify invoice exists in WHMCS mirror
        # ---------------------------------------------------
        whmcs_invoice = frappe.db.sql(
            """
            SELECT id
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
            LIMIT 1
            """,
            (relid,),
            as_dict=True,
        )

        if not whmcs_invoice:
            return False, "SKIP_MISSING_WHMCS_INVOICE"

        # ---------------------------------------------------
        # Verify Sales Invoice exists in ERP
        # ---------------------------------------------------
        invoice = frappe.db.get_value(
            "Sales Invoice",
            {"whmcs_invoice_id": str(relid)},
            ["name", "docstatus"],
            as_dict=True,
        )

        if not invoice:
            return False, "SKIP_MISSING_ERP_INVOICE"

        # ---------------------------------------------------
        # Cancelled invoice cannot receive credits
        # ---------------------------------------------------
        if invoice.docstatus == 2:
            return False, "SKIP_CANCELLED_INVOICE"

        return True, None
