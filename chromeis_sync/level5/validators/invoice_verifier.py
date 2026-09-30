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

        source_mode = evidence.get(
            "source_mode"
        )

        historical_snapshot = (
            source_mode
            == "HISTORICAL_SNAPSHOT"
        )

        live_post_snapshot = (
            source_mode
            == "LIVE_POST_SNAPSHOT"
        )

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
                if isinstance(t, dict)
            )
        )

        # ---------------------------------------------------------
        # Cancellation state
        #
        # A cancelled WHMCS invoice may retain its original invoice
        # total as "balance". That is not an outstanding ERP AR
        # balance when the ERP invoice is also cancelled.
        #
        # This must NOT suppress normal commercial/item validation.
        # It only prevents the cancelled invoice's displayed WHMCS
        # balance from being treated as an ERP outstanding mismatch.
        # ---------------------------------------------------------

        source_cancelled = (
            str(
                api.get("status") or ""
            ).strip().lower()
            == "cancelled"
        )

        if historical_snapshot:

            source_cancelled = (
                source_cancelled
                and
                str(
                    mirror.get("status") or ""
                ).strip().lower()
                == "cancelled"
            )

        cancelled_pair = (
            source_cancelled
            and
            int(
                erp.get("docstatus") or 0
            )
            == 2
        )

        # ---------------------------------------------------------
        # Commercial value verification
        # ---------------------------------------------------------

        if whmcs_credit > cls.TOLERANCE:

            cls._compare(
                differences,
                "gross_total",
                whmcs_subtotal + whmcs_tax,
                (
                    mirror.get("subtotal")
                    if historical_snapshot
                    else None
                ),
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
                    "classification": (
                        "TAX_PRESENTATION_ONLY"
                    ),
                    "whmcs_tax": float(
                        whmcs_tax
                    ),
                    "erp_tax": float(
                        erp_tax_total
                    ),
                })

            else:

                cls._compare(
                    differences,
                    "total",
                    api.get("total"),
                    (
                        mirror.get("total")
                        if historical_snapshot
                        else None
                    ),
                    erp_grand_total,
                )

        # ---------------------------------------------------------
        # Credit comparison
        # ---------------------------------------------------------

        if historical_snapshot:

            cls._compare(
                differences,
                "credit",
                api.get("credit"),
                mirror.get("credit"),
                None,
            )

        # ---------------------------------------------------------
        # Evidence collections
        # ---------------------------------------------------------

        whmcs_transactions = (
            evidence.get("whmcs_transactions")
            or []
        )

        erp_payments = (
            evidence.get("erp_payments")
            or []
        )

        whmcs_credits = (
            evidence.get("whmcs_credits")
            or []
        )

        erp_journals = (
            evidence.get("erp_journals")
            or []
        )

        # ---------------------------------------------------------
        # WHMCS API vs mirror transaction completeness
        #
        # WHMCS may return transactions in different shapes:
        #
        #   {"transaction": {...}}
        #   {"transaction": [{...}, {...}]}
        #   ""
        #   None
        #
        # Never assume transactions is a dictionary.
        # ---------------------------------------------------------

        api_transactions_container = (
            api.get("transactions")
        )

        if isinstance(
            api_transactions_container,
            dict,
        ):

            api_transactions = (
                api_transactions_container.get(
                    "transaction",
                    [],
                )
            )

        else:

            api_transactions = []

        if isinstance(
            api_transactions,
            dict,
        ):

            api_transactions = [
                api_transactions
            ]

        elif not isinstance(
            api_transactions,
            list,
        ):

            api_transactions = []

        api_transaction_ids = {
            str(row.get("id"))
            for row in api_transactions
            if isinstance(row, dict)
            and row.get("id") is not None
        }

        mirror_transaction_ids = {
            str(row.get("id"))
            for row in whmcs_transactions
            if isinstance(row, dict)
            and row.get("id") is not None
        }

        if historical_snapshot:

            missing_mirror_transaction_ids = (
                api_transaction_ids
                - mirror_transaction_ids
            )

            extra_mirror_transaction_ids = (
                mirror_transaction_ids
                - api_transaction_ids
            )

            transaction_population_complete = (
                not missing_mirror_transaction_ids
            )

            if (
                missing_mirror_transaction_ids
                or extra_mirror_transaction_ids
            ):

                differences.append({
                    "field": (
                        "whmcs_transaction_population"
                    ),
                    "source": (
                        "WHMCS_API_vs_WHMCS_MIRROR"
                    ),
                    "classification": (
                        "ERP_DIFFERENCE"
                    ),
                    "api_transaction_count": len(
                        api_transaction_ids
                    ),
                    "mirror_transaction_count": len(
                        mirror_transaction_ids
                    ),
                    "missing_mirror_transaction_ids": sorted(
                        missing_mirror_transaction_ids
                    ),
                    "extra_mirror_transaction_ids": sorted(
                        extra_mirror_transaction_ids
                    ),
                })

        else:

            # Post-snapshot transaction evidence originates from
            # the live GetInvoice response itself. Do not create a
            # meaningless API-vs-API completeness comparison.
            transaction_population_complete = True

        # ---------------------------------------------------------
        # Payment relationship calculations
        # ---------------------------------------------------------

        whmcs_payment_amount = sum(
            (
                cls._decimal(
                    row.get("amountin")
                )
                for row in whmcs_transactions
                if isinstance(row, dict)
            ),
            Decimal("0"),
        )

        # Invoice-linked payments prove allocation. For live
        # post-snapshot evidence, transaction-linked payments prove
        # receipt parity, including legitimate unallocated overpayments.
        payment_population = (
            evidence.get("erp_transaction_payments") or []
            if live_post_snapshot
            else erp_payments
        )

        erp_payment_amount = sum(
            (
                cls._decimal(
                    row.get("paid_amount")
                )
                for row in payment_population
                if isinstance(row, dict)
            ),
            Decimal("0"),
        )

        payment_matched = (
            round(
                whmcs_payment_amount,
                2,
            )
            == round(
                erp_payment_amount,
                2,
            )
        )

        # ---------------------------------------------------------
        # Credit relationship calculations
        # ---------------------------------------------------------

        whmcs_credit_amount = sum(
            (
                abs(
                    cls._decimal(
                        row.get("amount") or 0
                    )
                )
                for row in whmcs_credits
                if isinstance(row, dict)
            ),
            Decimal("0"),
        )

        erp_credit_ids = {
            str(
                row.get(
                    "custom_whmcs_credit_id"
                )
            )
            for row in erp_journals
            if isinstance(row, dict)
            and row.get(
                "custom_whmcs_credit_id"
            )
        }

        whmcs_credit_ids = {
            str(row.get("id"))
            for row in whmcs_credits
            if isinstance(row, dict)
            and row.get("id") is not None
            and cls._decimal(row.get("amount")) != Decimal("0")
        }

        credit_journal_matched = (
            not whmcs_credit_ids
            or whmcs_credit_ids.issubset(
                erp_credit_ids
            )
        )

        # ---------------------------------------------------------
        # Overpayment calculation
        # ---------------------------------------------------------

        overpayment_amount = (
            whmcs_payment_amount
            - whmcs_total
        )

        overpayment_matches_credit = (
            overpayment_amount
            > cls.TOLERANCE
            and
            round(
                overpayment_amount,
                2,
            )
            ==
            round(
                whmcs_credit_amount,
                2,
            )
        )

        # ---------------------------------------------------------
        # ERP payment allocation
        # ---------------------------------------------------------

        erp_invoice_total = (
            erp_grand_total
        )

        erp_allocated_amount = sum(
            (
                cls._decimal(
                    row.get(
                        "allocated_amount"
                    )
                )
                for row in erp_payments
                if isinstance(row, dict)
            ),
            Decimal("0"),
        )

        allocation_matches_invoice = (
            round(
                erp_allocated_amount,
                2,
            )
            ==
            round(
                erp_invoice_total,
                2,
            )
        )

        # ---------------------------------------------------------
        # Outstanding balance
        #
        # IMPORTANT:
        # A cancelled WHMCS invoice can retain its original amount
        # as the displayed "balance". When both WHMCS and ERP agree
        # that the invoice is cancelled, this is not an outstanding
        # ERP receivable and must not create an ERP_DIFFERENCE.
        #
        # For normal invoices, the existing balance / credit /
        # overpayment logic remains unchanged.
        # ---------------------------------------------------------

        if not cancelled_pair:

            if (
                whmcs_credit <= cls.TOLERANCE
                and cls._decimal(
                    api.get("balance")
                ) < -cls.TOLERANCE
                and transaction_population_complete
                and payment_matched
                and overpayment_matches_credit
                and allocation_matches_invoice
                and credit_journal_matched
            ):

                differences.append({
                    "field": "balance",
                    "source": "WHMCS_API_vs_ERP",
                    "classification": (
                        "WHMCS_CREDIT_PRESENTATION_ONLY"
                    ),
                    "api": api.get("balance"),
                    "mirror": None,
                    "erp": erp.get(
                        "outstanding_amount"
                    ),
                    "whmcs_payment_amount": float(
                        whmcs_payment_amount
                    ),
                    "whmcs_invoice_total": float(
                        whmcs_total
                    ),
                    "whmcs_credit_amount": float(
                        whmcs_credit_amount
                    ),
                    "erp_payment_amount": float(
                        erp_payment_amount
                    ),
                    "erp_allocated_amount": float(
                        erp_allocated_amount
                    ),
                    "credit_journal_matched": (
                        credit_journal_matched
                    ),
                    "transaction_population_complete": (
                        transaction_population_complete
                    ),
                })

            elif (
                whmcs_credit <= cls.TOLERANCE
                and not any(
                    d.get("classification")
                    == "TAX_PRESENTATION_ONLY"
                    for d in differences
                    if isinstance(d, dict)
                )
            ):

                cls._compare(
                    differences,
                    "balance",
                    api.get("balance"),
                    None,
                    erp.get(
                        "outstanding_amount"
                    ),
                )

        # ---------------------------------------------------------
        # Customer identity
        # ---------------------------------------------------------

        if historical_snapshot:

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
                "classification": (
                    "TAX_PRESENTATION_ONLY"
                ),
                "whmcs_tax": float(
                    whmcs_tax
                ),
                "erp_tax": float(
                    erp_tax_total
                ),
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
        # Payment relationship verification
        # ---------------------------------------------------------

        payment_differences = (
            cls._verify_payment_relationship(
                evidence
            )
        )

        differences.extend(
            payment_differences
        )

        # ---------------------------------------------------------
        # Credit relationship verification
        # ---------------------------------------------------------

        credit_differences = (
            cls._verify_credit_relationship(
                evidence
            )
        )

        differences.extend(
            credit_differences
        )

        relationship_evidence = {
            "payment": (
                "EXCEPTION"
                if payment_differences
                else "MATCHED"
            ),
            "credit": (
                "EXCEPTION"
                if credit_differences
                else "MATCHED"
            ),
        }

        # ---------------------------------------------------------
        # Final blocking classification
        # ---------------------------------------------------------

        blocking_differences = [
            d
            for d in differences
            if isinstance(d, dict)
            and not (
                cancelled_pair
                and d.get("field") == "items"
            )
            and d.get("classification")
            not in (
                "TAX_PRESENTATION_ONLY",
                "WHMCS_CREDIT_PRESENTATION_ONLY",
            )
        ]

        return {
            "whmcs_id": evidence["whmcs_id"],
            "erp_id": evidence["erp_id"],
            "status": (
                "VERIFIED"
                if not blocking_differences
                else "ERP_DIFFERENCE"
            ),
            "differences": differences,
            "relationship_evidence": relationship_evidence,
        }

    # -------------------------------------------------------------
    # Payment relationship verification
    # -------------------------------------------------------------

    @staticmethod
    def _verify_payment_relationship(evidence):

        differences = []

        whmcs_transactions = (
            evidence.get("whmcs_transactions")
            or []
        )

        erp_payments = (
            evidence.get("erp_payments")
            or []
        )

        source_mode = evidence.get(
            "source_mode"
        )

        # ---------------------------------------------------------
        # Historical snapshot behavior
        #
        # Preserve the existing Level-5 relationship rule exactly.
        # Historical payment evidence is still compared through
        # invoice allocation.
        # ---------------------------------------------------------

        if source_mode == "HISTORICAL_SNAPSHOT":

            whmcs_amount = sum(
                float(row.get("amountin") or 0)
                for row in whmcs_transactions
                if isinstance(row, dict)
            )

            erp_amount = sum(
                float(row.get("paid_amount") or 0)
                for row in erp_payments
                if isinstance(row, dict)
            )

            if round(
                whmcs_amount,
                2,
            ) != round(
                erp_amount,
                2,
            ):

                differences.append({
                    "field": "payment_relationship",
                    "source": (
                        "WHMCS_transactions_vs_ERP_payment_entries"
                    ),
                    "whmcs_amount": whmcs_amount,
                    "erp_amount": erp_amount,
                })

            return differences

        # ---------------------------------------------------------
        # Live post-snapshot behavior
        #
        # Reconcile source transaction identity independently from
        # invoice allocation. A WHMCS receipt may legitimately be
        # partly or wholly unallocated to this Sales Invoice.
        # ---------------------------------------------------------

        if source_mode != "LIVE_POST_SNAPSHOT":

            differences.append({
                "field": "payment_relationship",
                "source": "SOURCE_PROVENANCE",
                "classification": "ERP_DIFFERENCE",
                "reason": (
                    "Unsupported source mode for "
                    "payment relationship verification."
                ),
            })

            return differences

        erp_transaction_payments = (
            evidence.get(
                "erp_transaction_payments"
            )
            or []
        )

        payments_by_txn_id = {}

        for payment in erp_transaction_payments:

            if not isinstance(
                payment,
                dict,
            ):
                continue

            txn_id = payment.get(
                "custom_whmcs_txn_id"
            )

            if not txn_id:
                continue

            txn_id = str(txn_id)

            if txn_id not in payments_by_txn_id:
                payments_by_txn_id[txn_id] = []

            payments_by_txn_id[txn_id].append(
                payment
            )

        for transaction in whmcs_transactions:

            if not isinstance(
                transaction,
                dict,
            ):
                continue

            txn_id = transaction.get("id")

            if not txn_id:

                differences.append({
                    "field": "payment_relationship",
                    "source": "WHMCS_LIVE_API",
                    "classification": "ERP_DIFFERENCE",
                    "reason": (
                        "Live WHMCS transaction "
                        "identity is missing."
                    ),
                })

                continue

            txn_id = str(txn_id)

            matches = payments_by_txn_id.get(
                txn_id,
                [],
            )

            if not matches:

                differences.append({
                    "field": "payment_relationship",
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_payment_identity"
                    ),
                    "classification": "ERP_DIFFERENCE",
                    "whmcs_transaction_id": txn_id,
                    "whmcs_amount": float(
                        transaction.get(
                            "amountin"
                        )
                        or 0
                    ),
                    "erp_payment_found": False,
                })

                continue

            if len(matches) != 1:

                differences.append({
                    "field": "payment_relationship",
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_payment_identity"
                    ),
                    "classification": "ERP_DIFFERENCE",
                    "whmcs_transaction_id": txn_id,
                    "erp_match_count": len(matches),
                    "reason": (
                        "WHMCS transaction identity "
                        "is not unique in ERP."
                    ),
                })

                continue

            payment = matches[0]

            if int(
                payment.get("docstatus") or 0
            ) != 1:

                differences.append({
                    "field": "payment_relationship",
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_payment_identity"
                    ),
                    "classification": "ERP_DIFFERENCE",
                    "whmcs_transaction_id": txn_id,
                    "erp_payment": payment.get(
                        "name"
                    ),
                    "reason": (
                        "Matching ERP Payment Entry "
                        "is not submitted."
                    ),
                })

                continue

            whmcs_amount = Decimal(
                str(
                    transaction.get(
                        "amountin"
                    )
                    or 0
                )
            )

            erp_amount = Decimal(
                str(
                    payment.get(
                        "paid_amount"
                    )
                    or 0
                )
            )

            if (
                abs(
                    whmcs_amount
                    - erp_amount
                )
                > Decimal("0.0001")
            ):

                differences.append({
                    "field": "payment_relationship",
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_payment_identity"
                    ),
                    "classification": "ERP_DIFFERENCE",
                    "whmcs_transaction_id": txn_id,
                    "erp_payment": payment.get(
                        "name"
                    ),
                    "whmcs_amount": float(
                        whmcs_amount
                    ),
                    "erp_amount": float(
                        erp_amount
                    ),
                    "reason": (
                        "WHMCS transaction amount "
                        "does not match ERP Payment Entry."
                    ),
                })

        return differences

    # -------------------------------------------------------------
    # Credit relationship verification
    # -------------------------------------------------------------

    @staticmethod
    def _verify_credit_relationship(evidence):

        differences = []

        whmcs_credits = (
            evidence.get("whmcs_credits")
            or []
        )

        if not whmcs_credits:
            return differences

        erp_journals = (
            evidence.get("erp_journals")
            or []
        )

        source_mode = evidence.get(
            "source_mode"
        )

        erp_invoice_id = str(
            evidence.get("erp_id") or ""
        )

        journals_by_credit_id = {}

        for journal in erp_journals:

            if not isinstance(
                journal,
                dict,
            ):
                continue

            credit_id = journal.get(
                "custom_whmcs_credit_id"
            )

            if credit_id:

                credit_id = str(credit_id)

                if credit_id not in journals_by_credit_id:
                    journals_by_credit_id[credit_id] = []

                journals_by_credit_id[
                    credit_id
                ].append(journal)

        # ---------------------------------------------------------
        # Historical snapshot behavior
        #
        # Preserve the existing Level-5 rule exactly: every
        # non-zero WHMCS mirror credit must have a corresponding
        # ERP Journal Entry identity.
        # ---------------------------------------------------------

        if source_mode == "HISTORICAL_SNAPSHOT":

            for credit in whmcs_credits:

                if not isinstance(
                    credit,
                    dict,
                ):
                    continue

                amount = Decimal(
                    str(
                        credit.get("amount")
                        or 0
                    )
                )

                if amount == Decimal("0"):
                    continue

                credit_id = str(
                    credit.get("id")
                )

                if (
                    credit_id
                    not in journals_by_credit_id
                ):

                    differences.append({
                        "field": (
                            "credit_relationship"
                        ),
                        "source": (
                            "WHMCS_credit_vs_ERP_journal"
                        ),
                        "whmcs_credit_id": (
                            credit_id
                        ),
                        "whmcs_amount": abs(
                            float(amount)
                        ),
                        "erp_journal_found": False,
                    })

            return differences

        # ---------------------------------------------------------
        # Live post-snapshot behavior
        #
        # Credit Applied:
        #   consumes customer deposit and must reference this SI.
        #
        # Overpayment:
        #   creates/adjusts customer deposit and must NOT reference
        #   this SI.
        #
        # Unknown lifecycle:
        #   fail closed. Do not inherit the sync router's temporary
        #   fallback-to-overpayment behavior.
        # ---------------------------------------------------------

        if source_mode != "LIVE_POST_SNAPSHOT":

            differences.append({
                "field": "credit_relationship",
                "source": "SOURCE_PROVENANCE",
                "classification": "ERP_DIFFERENCE",
                "reason": (
                    "Unsupported source mode for "
                    "credit relationship verification."
                ),
            })

            return differences

        for credit in whmcs_credits:

            if not isinstance(
                credit,
                dict,
            ):
                continue

            amount = Decimal(
                str(
                    credit.get("amount")
                    or 0
                )
            )

            if amount == Decimal("0"):
                continue

            credit_id = str(
                credit.get("id")
            )

            description = str(
                credit.get("description")
                or ""
            ).strip().lower()

            if "credit applied" in description:
                lifecycle = "CREDIT_APPLIED"
            elif "overpayment" in description:
                lifecycle = "OVERPAYMENT"
            else:
                lifecycle = "UNRECOGNIZED"

            if lifecycle == "UNRECOGNIZED":

                differences.append({
                    "field": (
                        "credit_relationship"
                    ),
                    "source": (
                        "WHMCS_LIVE_API"
                    ),
                    "classification": (
                        "ERP_DIFFERENCE"
                    ),
                    "whmcs_credit_id": (
                        credit_id
                    ),
                    "whmcs_amount": float(
                        amount
                    ),
                    "reason": (
                        "Unrecognized live WHMCS "
                        "credit lifecycle."
                    ),
                })

                continue

            matches = journals_by_credit_id.get(
                credit_id,
                [],
            )

            if not matches:

                differences.append({
                    "field": (
                        "credit_relationship"
                    ),
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_journal"
                    ),
                    "classification": (
                        "ERP_DIFFERENCE"
                    ),
                    "whmcs_credit_id": (
                        credit_id
                    ),
                    "whmcs_amount": float(
                        amount
                    ),
                    "lifecycle": lifecycle,
                    "erp_journal_found": False,
                })

                continue

            if len(matches) != 1:

                differences.append({
                    "field": "credit_relationship",
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_journal_identity"
                    ),
                    "classification": "ERP_DIFFERENCE",
                    "whmcs_credit_id": credit_id,
                    "erp_match_count": len(matches),
                    "reason": (
                        "WHMCS credit identity "
                        "is not unique in ERP."
                    ),
                })

                continue

            journal = matches[0]

            if int(
                journal.get("docstatus") or 0
            ) != 1:

                differences.append({
                    "field": (
                        "credit_relationship"
                    ),
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_journal"
                    ),
                    "classification": (
                        "ERP_DIFFERENCE"
                    ),
                    "whmcs_credit_id": (
                        credit_id
                    ),
                    "lifecycle": lifecycle,
                    "erp_journal": (
                        journal.get("name")
                    ),
                    "reason": (
                        "Matching ERP Journal Entry "
                        "is not submitted."
                    ),
                })

                continue

            accounts = (
                journal.get("accounts")
                or []
            )

            references_invoice = any(
                isinstance(row, dict)
                and row.get(
                    "reference_type"
                ) == "Sales Invoice"
                and str(
                    row.get(
                        "reference_name"
                    )
                    or ""
                ) == erp_invoice_id
                for row in accounts
            )

            if (
                lifecycle == "CREDIT_APPLIED"
                and not references_invoice
            ):

                differences.append({
                    "field": (
                        "credit_invoice_allocation"
                    ),
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_journal"
                    ),
                    "classification": (
                        "ERP_DIFFERENCE"
                    ),
                    "whmcs_credit_id": (
                        credit_id
                    ),
                    "lifecycle": lifecycle,
                    "erp_journal": (
                        journal.get("name")
                    ),
                    "reason": (
                        "Credit Applied journal does "
                        "not reference the ERP invoice."
                    ),
                })

            if (
                lifecycle == "OVERPAYMENT"
                and references_invoice
            ):

                differences.append({
                    "field": (
                        "credit_invoice_allocation"
                    ),
                    "source": (
                        "WHMCS_LIVE_API_vs_ERP_journal"
                    ),
                    "classification": (
                        "ERP_DIFFERENCE"
                    ),
                    "whmcs_credit_id": (
                        credit_id
                    ),
                    "lifecycle": lifecycle,
                    "erp_journal": (
                        journal.get("name")
                    ),
                    "reason": (
                        "Overpayment journal must not "
                        "reference the ERP invoice."
                    ),
                })

        return differences

    # -------------------------------------------------------------
    # Numeric comparison
    # -------------------------------------------------------------

    @staticmethod
    def _compare(
        differences,
        field,
        api,
        mirror,
        erp,
    ):

        if erp is None:
            return

        if round(
            float(api or 0),
            4,
        ) != round(
            float(erp or 0),
            4,
        ):

            differences.append({
                "field": field,
                "source": "WHMCS_API_vs_ERP",
                "api": api,
                "mirror": mirror,
                "erp": erp,
            })

    # -------------------------------------------------------------
    # Decimal helper
    # -------------------------------------------------------------

    @staticmethod
    def _decimal(value):

        return Decimal(
            str(value or 0)
        )
