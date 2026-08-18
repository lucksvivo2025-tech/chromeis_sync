from decimal import Decimal

import frappe

from chromeis_sync.level5.validators.item_verifier import (
    ItemVerifier,
)


class InvoiceVerifier:

    TOLERANCE = Decimal("0.0001")

    @classmethod
    def verify(cls, evidence):

        api = evidence["api"]
        mirror = evidence["mirror"] or {}
        erp = evidence["erp"]

        differences = []

        whmcs_credit = cls._decimal(
            api.get("credit")
        )

        whmcs_subtotal = cls._decimal(
            api.get("subtotal")
        )

        whmcs_total = cls._decimal(
            api.get("total")
        )

        whmcs_tax = cls._decimal(
            api.get("tax")
        )

        erp_grand_total = cls._decimal(
            erp.get("grand_total")
        )

        erp_net_total = cls._decimal(
            erp.get("net_total")
        )

        erp_tax_total = cls._decimal(
            sum(
                t.get("tax_amount", 0)
                for t in erp.get("taxes", [])
            )
        )


        # ---------------------------------------------------------
        # Commercial value verification
        #
        # ERP may store subtotal only while WHMCS stores
        # subtotal + tax.
        #
        # This is presentation difference, not financial difference.
        # ---------------------------------------------------------

        if whmcs_credit > cls.TOLERANCE:

            cls._compare(
                differences,
                "gross_total",
                api.get("subtotal"),
                mirror.get("subtotal"),
                erp.get("grand_total"),
            )

        else:

            if (
                whmcs_tax > cls.TOLERANCE
                and
                whmcs_subtotal == erp_net_total
                and
                erp_tax_total == 0
            ):

                differences.append({
                    "field": "tax",
                    "source": "WHMCS_API_vs_ERP",
                    "classification": "TAX_PRESENTATION_ONLY",
                    "whmcs_tax": float(whmcs_tax),
                    "erp_tax": float(erp_tax_total),
                })

            else:

                cls._compare(
                    differences,
                    "total",
                    api.get("total"),
                    mirror.get("total"),
                    erp_grand_total,
                )


        # ---------------------------------------------------------
        # Credit comparison
        # ---------------------------------------------------------

        cls._compare(
            differences,
            "credit",
            api.get("credit"),
            mirror.get("credit"),
            None,
        )


        # ---------------------------------------------------------
        # Outstanding balance
        #
        # Ignore balance difference caused only by tax presentation.
        # ---------------------------------------------------------

        if (
            whmcs_credit <= cls.TOLERANCE
            and not any(
                d.get("classification")
                == "TAX_PRESENTATION_ONLY"
                for d in differences
            )
        ):

            cls._compare(
                differences,
                "balance",
                api.get("balance"),
                None,
                erp.get("outstanding_amount"),
            )


        # ---------------------------------------------------------
        # Customer identity
        # ---------------------------------------------------------

        cls._compare(
            differences,
            "customer",
            api.get("userid"),
            mirror.get("userid"),
            None,
        )


        # ---------------------------------------------------------
        # Tax evidence
        # ---------------------------------------------------------

        if (
            whmcs_tax > cls.TOLERANCE
            and erp_tax_total == 0
        ):

            differences.append({
                "field": "tax_structure",
                "classification": "TAX_PRESENTATION_ONLY",
                "whmcs_tax": float(whmcs_tax),
                "erp_tax": float(erp_tax_total),
            })


        # ---------------------------------------------------------
        # Invoice item verification
        # ---------------------------------------------------------

        item_differences = ItemVerifier.verify(
            api.get("items", {}),
            erp.get("items", []),
        )

        differences.extend(
            item_differences
        )


        # ---------------------------------------------------------
        # WHMCS Credit Application
        # ---------------------------------------------------------

        if whmcs_credit > cls.TOLERANCE:

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
                        "whmcs_credit_id":
                            credit_evidence["whmcs_credit_id"],
                        "whmcs_amount":
                            float(
                                credit_evidence["amount"]
                            ),
                        "erp_credit_found": False,
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


    @staticmethod
    def _compare(differences, field, api, mirror, erp):

        if erp is None:
            return

        if round(float(api or 0), 4) != round(float(erp or 0), 4):

            differences.append({
                "field": field,
                "source": "WHMCS_API_vs_ERP",
                "api": api,
                "mirror": mirror,
                "erp": erp,
            })


    @staticmethod
    def _decimal(value):

        return Decimal(
            str(value or 0)
        )


    @staticmethod
    def _find_credit_application(invoice_id):

        rows = frappe.db.sql(
            """
            SELECT
                id,
                amount
            FROM whmcs_mirror.tblcredit
            WHERE relid=%s
            AND amount < 0
            """,
            (str(invoice_id),),
            as_dict=True,
        )

        if not rows:
            return None

        return {
            "whmcs_credit_id": str(rows[0]["id"]),
            "amount": sum(
                abs(
                    float(r["amount"])
                )
                for r in rows
            )
        }


    @staticmethod
    def _find_erp_credit(whmcs_credit_id):

        return frappe.db.sql(
            """
            SELECT
                name
            FROM `tabJournal Entry`
            WHERE custom_whmcs_credit_id=%s
            LIMIT 1
            """,
            (str(whmcs_credit_id),),
            as_dict=True,
        )
