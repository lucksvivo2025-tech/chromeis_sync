import frappe

from chromeis_sync.level5.api.client import Level5WHMCSClient
from chromeis_sync.level5.source_evidence_policy import (
    SourceEvidencePolicy,
)


class InvoiceCollector:

    @staticmethod
    def collect(whmcs_invoice_id, erp_invoice_id):

        api_client = Level5WHMCSClient()

        # ---------------------------------------------------------
        # WHMCS API
        # ---------------------------------------------------------

        api = api_client.get_invoice(
            whmcs_invoice_id
        )

        source_mode = SourceEvidencePolicy.source_mode(
            whmcs_invoice_id
        )

        mirror_applicable = (
            source_mode
            == SourceEvidencePolicy.HISTORICAL_SNAPSHOT
        )

        # ---------------------------------------------------------
        # WHMCS Mirror - Invoice
        # ---------------------------------------------------------

        mirror = None

        if mirror_applicable:

            mirror_rows = frappe.db.sql(
                """
                SELECT *
                FROM whmcs_mirror.tblinvoices
                WHERE id=%s
                LIMIT 1
                """,
                (whmcs_invoice_id,),
                as_dict=True,
            )

            mirror = (
                mirror_rows[0]
                if mirror_rows
                else None
            )

        # ---------------------------------------------------------
        # WHMCS Mirror - Transactions
        # ---------------------------------------------------------

        if mirror_applicable:

            whmcs_transactions = frappe.db.sql(
                """
                SELECT *
                FROM whmcs_mirror.tblaccounts
                WHERE invoiceid=%s
                ORDER BY id
                """,
                (whmcs_invoice_id,),
                as_dict=True,
            )

        else:

            transactions_container = (
                api.get("transactions")
                if isinstance(api, dict)
                else None
            )

            if isinstance(
                transactions_container,
                dict,
            ):
                live_transactions = (
                    transactions_container.get(
                        "transaction",
                        [],
                    )
                )
            else:
                live_transactions = []

            if isinstance(
                live_transactions,
                dict,
            ):
                whmcs_transactions = [
                    live_transactions
                ]
            elif isinstance(
                live_transactions,
                list,
            ):
                whmcs_transactions = (
                    live_transactions
                )
            else:
                whmcs_transactions = []

        # ---------------------------------------------------------
        # WHMCS Mirror - Credits
        #
        # tblcredit uses relid for the related invoice.
        # Keep the complete rows as forensic evidence.
        # ---------------------------------------------------------

        if mirror_applicable:

            whmcs_credits = frappe.db.sql(
                """
                SELECT *
                FROM whmcs_mirror.tblcredit
                WHERE relid=%s
                ORDER BY id
                """,
                (str(whmcs_invoice_id),),
                as_dict=True,
            )

        else:

            whmcs_credits = []

            client_id = (
                api.get("userid")
                if isinstance(api, dict)
                else None
            )

            if client_id:

                credits_response = (
                    api_client.get_credits(
                        client_id
                    )
                )

                credits_container = (
                    credits_response.get(
                        "credits",
                        {}
                    )
                    if isinstance(
                        credits_response,
                        dict,
                    )
                    else {}
                )

                if isinstance(
                    credits_container,
                    dict,
                ):
                    live_credits = (
                        credits_container.get(
                            "credit",
                            []
                        )
                    )
                else:
                    live_credits = []

                if isinstance(
                    live_credits,
                    dict,
                ):
                    live_credits = [
                        live_credits
                    ]

                if isinstance(
                    live_credits,
                    list,
                ):

                    for credit in live_credits:

                        if not isinstance(
                            credit,
                            dict,
                        ):
                            continue

                        if str(
                            credit.get("relid")
                            or ""
                        ) == str(
                            whmcs_invoice_id
                        ):
                            whmcs_credits.append(
                                credit
                            )

        # ---------------------------------------------------------
        # ERP Invoice
        # ---------------------------------------------------------

        erp = frappe.get_doc(
            "Sales Invoice",
            erp_invoice_id,
        )

        # ---------------------------------------------------------
        # ERP Payments
        #
        # Collect payments through Payment Entry Reference so
        # relationship evidence reflects actual ERP allocation.
        # ---------------------------------------------------------

        erp_payments = frappe.db.sql(
            """
            SELECT
                pe.name,
                pe.party,
                pe.party_type,
                pe.paid_amount,
                pe.received_amount,
                pe.posting_date,
                pe.docstatus,
                per.reference_name,
                per.allocated_amount
            FROM `tabPayment Entry Reference` per
            INNER JOIN `tabPayment Entry` pe
                ON pe.name = per.parent
            WHERE
                per.reference_doctype = 'Sales Invoice'
                AND per.reference_name = %s
            ORDER BY pe.name
            """,
            (erp_invoice_id,),
            as_dict=True,
        )

        # ---------------------------------------------------------
        # ERP Payments by WHMCS Transaction Identity
        #
        # This is separate from erp_payments above. erp_payments
        # proves invoice allocation through Payment Entry Reference.
        # This population proves whether the source WHMCS transaction
        # itself exists in ERP, including receipts intentionally left
        # unallocated to the Sales Invoice.
        # ---------------------------------------------------------

        transaction_ids = []

        for row in whmcs_transactions:

            if not isinstance(row, dict):
                continue

            transaction_id = row.get("id")

            if transaction_id:
                transaction_ids.append(
                    str(transaction_id)
                )

        erp_transaction_payments = []

        if transaction_ids:

            placeholders = ", ".join(
                ["%s"] * len(transaction_ids)
            )

            erp_transaction_payments = frappe.db.sql(
                f"""
                SELECT
                    name,
                    party,
                    party_type,
                    paid_amount,
                    received_amount,
                    posting_date,
                    docstatus,
                    custom_whmcs_txn_id,
                    reference_no,
                    unallocated_amount
                FROM `tabPayment Entry`
                WHERE custom_whmcs_txn_id IN ({placeholders})
                ORDER BY name
                """,
                tuple(transaction_ids),
                as_dict=True,
            )

            for payment in erp_transaction_payments:

                payment["references"] = frappe.db.sql(
                    """
                    SELECT
                        reference_doctype,
                        reference_name,
                        allocated_amount
                    FROM `tabPayment Entry Reference`
                    WHERE parent=%s
                    ORDER BY idx
                    """,
                    (payment.get("name"),),
                    as_dict=True,
                )

        # ---------------------------------------------------------
        # ERP Credit Journals
        # ---------------------------------------------------------

        credit_ids = [
            str(row.get("id"))
            for row in whmcs_credits
            if row.get("id")
        ]

        erp_journals = []

        if credit_ids:

            placeholders = ", ".join(
                ["%s"] * len(credit_ids)
            )

            erp_journals = frappe.db.sql(
                f"""
                SELECT
                    name,
                    posting_date,
                    docstatus,
                    custom_whmcs_credit_id,
                    user_remark
                FROM `tabJournal Entry`
                WHERE custom_whmcs_credit_id IN ({placeholders})
                ORDER BY name
                """,
                tuple(credit_ids),
                as_dict=True,
            )

            for journal in erp_journals:

                journal["accounts"] = frappe.db.sql(
                    """
                    SELECT
                        account,
                        party_type,
                        party,
                        debit_in_account_currency,
                        credit_in_account_currency,
                        account_currency,
                        reference_type,
                        reference_name
                    FROM `tabJournal Entry Account`
                    WHERE parent=%s
                    ORDER BY idx
                    """,
                    (journal.get("name"),),
                    as_dict=True,
                )

        # ---------------------------------------------------------
        # ERP GL
        # ---------------------------------------------------------

        erp_gl = frappe.db.sql(
            """
            SELECT
                name,
                account,
                debit,
                credit,
                party_type,
                party,
                against,
                posting_date,
                voucher_type,
                voucher_no
            FROM `tabGL Entry`
            WHERE voucher_no=%s
            ORDER BY account, name
            """,
            (erp_invoice_id,),
            as_dict=True,
        )

        # ---------------------------------------------------------
        # ERP Invoice Evidence
        # ---------------------------------------------------------

        erp_evidence = {
            "name": erp.name,
            "customer": erp.customer,
            "posting_date": str(
                erp.posting_date
            ),
            "due_date": str(
                erp.due_date
            ),
            "currency": erp.currency,
            "conversion_rate": float(
                erp.conversion_rate or 0
            ),
            "total": float(
                erp.total or 0
            ),
            "net_total": float(
                erp.net_total or 0
            ),
            "grand_total": float(
                erp.grand_total or 0
            ),
            "outstanding_amount": float(
                erp.outstanding_amount or 0
            ),
            "discount_amount": float(
                erp.discount_amount or 0
            ),
            "status": erp.status,
            "docstatus": erp.docstatus,

            "items": [
                {
                    "item_code": item.item_code,
                    "description": item.description,
                    "qty": float(
                        item.qty or 0
                    ),
                    "rate": float(
                        item.rate or 0
                    ),
                    "amount": float(
                        item.amount or 0
                    ),
                    "net_amount": float(
                        item.net_amount or 0
                    ),
                    "income_account": (
                        item.income_account
                    ),
                    "cost_center": (
                        item.cost_center
                    ),
                }
                for item in erp.items
            ],

            "taxes": [
                {
                    "account_head": tax.account_head,
                    "rate": float(
                        tax.rate or 0
                    ),
                    "tax_amount": float(
                        tax.tax_amount or 0
                    ),
                    "total": float(
                        tax.total or 0
                    ),
                }
                for tax in erp.taxes
            ],

            "gl_entries": erp_gl,
        }

        # ---------------------------------------------------------
        # Complete evidence contract
        # ---------------------------------------------------------

        return {
            "whmcs_id": str(
                whmcs_invoice_id
            ),

            "erp_id": erp_invoice_id,

            "source_mode": source_mode,

            "relationship_source": (
                "WHMCS_MIRROR"
                if mirror_applicable
                else "WHMCS_LIVE_API"
            ),

            "mirror_applicable": (
                mirror_applicable
            ),

            "api": api,

            "mirror": mirror,

            "whmcs_transactions": (
                whmcs_transactions
            ),

            "whmcs_credits": (
                whmcs_credits
            ),

            "erp_payments": (
                erp_payments
            ),

            "erp_transaction_payments": (
                erp_transaction_payments
            ),

            "erp_journals": (
                erp_journals
            ),

            "erp": erp_evidence,
        }
