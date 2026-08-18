from decimal import Decimal

import frappe


class InvoiceVerifier:

    TOLERANCE = Decimal("0.0001")

    @classmethod
    def verify(cls, evidence):

        api = evidence["api"]
        mirror = evidence["mirror"]
        erp = evidence["erp"]

        differences = []

        # ---------------------------------------------------------
        # Core amount comparisons
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # Core invoice total comparison
        #
        # WHMCS applies credits directly to invoice total.
        # ERP keeps the original invoice gross value and represents
        # credit separately through Journal Entry / allocation.
        #
        # Therefore:
        #   WHMCS subtotal == ERP grand_total
        # when WHMCS credit exists.
        # ---------------------------------------------------------

        whmcs_credit = cls._decimal(
            api.get("credit")
        )

        if whmcs_credit > cls.TOLERANCE:

            cls._compare(
                differences,
                "gross_total",
                api.get("subtotal"),
                mirror.get("subtotal") if mirror else None,
                erp.get("grand_total"),
            )

        else:

            cls._compare(
                differences,
                "total",
                api.get("total"),
                mirror.get("total") if mirror else None,
                erp.get("grand_total"),
            )

        cls._compare(
            differences,
            "credit",
            api.get("credit"),
            mirror.get("credit") if mirror else None,
            None,
        )

        # ---------------------------------------------------------
        # Balance comparison
        #
        # WHMCS balance includes applied credits.
        # ERP keeps invoice outstanding separately and represents
        # credits through Journal Entries / allocations.
        #
        # Therefore credit invoices are verified through the credit
        # migration section below, not outstanding amount comparison.
        # ---------------------------------------------------------

        if whmcs_credit <= cls.TOLERANCE:

            cls._compare(
                differences,
                "balance",
                api.get("balance"),
                None,
                erp.get("outstanding_amount"),
            )

        # ---------------------------------------------------------
        # Identity
        # ---------------------------------------------------------

        cls._compare(
            differences,
            "customer",
            api.get("userid"),
            mirror.get("userid") if mirror else None,
            None,
        )

        # ---------------------------------------------------------
        # Tax
        # ---------------------------------------------------------

        cls._compare(
            differences,
            "tax",
            api.get("tax"),
            mirror.get("tax") if mirror else None,
            None,
        )

        # ---------------------------------------------------------
        # WHMCS credit application
        # ---------------------------------------------------------

        credit_amount = cls._decimal(api.get("credit"))

        if credit_amount > cls.TOLERANCE:
            credit_evidence = cls._find_credit_application(
                evidence["whmcs_id"]
            )

            if credit_evidence:
                erp_credit = cls._find_erp_credit(
                    credit_evidence["whmcs_credit_id"]
                )

                if not erp_credit:
                    differences.append({
                        "field": "credit_migration",
                        "source": "WHMCS_vs_ERP",
                        "whmcs_credit_id": (
                            credit_evidence["whmcs_credit_id"]
                        ),
                        "whmcs_amount": float(
                            credit_evidence["amount"]
                        ),
                        "erp_credit_found": False,
                    })

                else:
                    allocation = cls._find_invoice_allocation(
                        evidence["erp_id"]
                    )

                    if not allocation:
                        differences.append({
                            "field": "credit_invoice_allocation",
                            "source": "WHMCS_vs_ERP",
                            "whmcs_credit_id": (
                                credit_evidence["whmcs_credit_id"]
                            ),
                            "whmcs_amount": float(
                                credit_evidence["amount"]
                            ),
                            "erp_journal_entry": (
                                erp_credit["journal_entry"]
                            ),
                            "erp_credit_amount": float(
                                erp_credit["amount"]
                            ),
                            "invoice_allocation_found": False,
                        })

        return {
            "whmcs_id": evidence["whmcs_id"],
            "erp_id": evidence["erp_id"],
            "status": (
                "VERIFIED"
                if not differences
                else "ERP_DIFFERENCE"
            ),
            "differences": differences,
        }

    # -------------------------------------------------------------
    # WHMCS credit evidence
    # -------------------------------------------------------------

    @staticmethod
    def _find_credit_application(invoice_id):

        rows = frappe.db.sql(
            """
            SELECT
                id,
                clientid,
                date,
                amount,
                description,
                relid
            FROM whmcs_mirror.tblcredit
            WHERE relid=%s
              AND amount < 0
            ORDER BY id
            """,
            (str(invoice_id),),
            as_dict=True,
        )

        if not rows:
            return None

        total = sum(
            (
                abs(
                    InvoiceVerifier._decimal(
                        row["amount"]
                    )
                )
                for row in rows
            ),
            Decimal("0"),
        )

        return {
            "whmcs_credit_id": str(rows[0]["id"]),
            "amount": total,
            "rows": rows,
        }

    # -------------------------------------------------------------
    # ERP credit representation
    # -------------------------------------------------------------

    @staticmethod
    def _find_erp_credit(whmcs_credit_id):

        rows = frappe.db.sql(
            """
            SELECT
                name,
                docstatus,
                custom_whmcs_credit_id,
                total_debit,
                total_credit
            FROM `tabJournal Entry`
            WHERE custom_whmcs_credit_id=%s
            ORDER BY name
            """,
            (str(whmcs_credit_id),),
            as_dict=True,
        )

        if not rows:
            return None

        row = rows[0]

        return {
            "journal_entry": row["name"],
            "docstatus": row["docstatus"],
            "amount": max(
                cls_decimal(row["total_debit"]),
                cls_decimal(row["total_credit"]),
            ),
        }

    # -------------------------------------------------------------
    # ERP invoice allocation
    # -------------------------------------------------------------

    @staticmethod
    def _find_invoice_allocation(invoice_id):

        rows = frappe.db.sql(
            """
            SELECT
                name,
                parent,
                reference_doctype,
                reference_name,
                allocated_amount
            FROM `tabPayment Entry Reference`
            WHERE reference_doctype='Sales Invoice'
              AND reference_name=%s

            UNION ALL

            SELECT
                name,
                parent,
                reference_type AS reference_doctype,
                reference_name,
                credit AS allocated_amount
            FROM `tabJournal Entry Account`
            WHERE reference_type='Sales Invoice'
              AND reference_name=%s
            """,
            (
                str(invoice_id),
                str(invoice_id),
            ),
            as_dict=True,
        )

        return rows or None

    # -------------------------------------------------------------
    # Comparison helpers
    # -------------------------------------------------------------

    @classmethod
    def _compare(
        cls,
        differences,
        field,
        api_value,
        mirror_value,
        erp_value,
    ):

        if api_value is not None and mirror_value is not None:

            if cls._different(api_value, mirror_value):

                differences.append({
                    "field": field,
                    "source": "WHMCS_API_vs_MIRROR",
                    "api": api_value,
                    "mirror": mirror_value,
                })

        if api_value is not None and erp_value is not None:

            if cls._different(api_value, erp_value):

                differences.append({
                    "field": field,
                    "source": "WHMCS_API_vs_ERP",
                    "api": api_value,
                    "erp": erp_value,
                })

    @classmethod
    def _different(cls, a, b):

        try:
            return abs(
                Decimal(str(a or 0))
                - Decimal(str(b or 0))
            ) > cls.TOLERANCE

        except Exception:
            return str(a) != str(b)

    @staticmethod
    def _decimal(value):

        try:
            return Decimal(str(value or 0))
        except Exception:
            return Decimal("0")


def cls_decimal(value):
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal("0")
