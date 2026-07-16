@staticmethod
def payments():

    whmcs = frappe.db.sql("""
        SELECT COUNT(*)
        FROM whmcs_mirror.tblaccounts
    """)[0][0]

    erp = frappe.db.count(
        "Payment Entry",
        {
            "custom_whmcs_txn_id": ["is", "set"]
        },
    )

    skipped = frappe.db.sql("""
        SELECT COUNT(*)
        FROM whmcs_mirror.tblaccounts

        WHERE
            amountin = 0
            OR invoiceid = 0
    """)[0][0]

    expected = whmcs - skipped

    return {
        "module": "Payments",
        "whmcs": expected,
        "erp": erp,
        "difference": expected - erp,
        "status": "PASS" if expected == erp else "FAIL",
    }
