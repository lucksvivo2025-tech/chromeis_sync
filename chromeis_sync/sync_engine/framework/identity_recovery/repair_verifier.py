import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_comparator import (
    InvoiceComparator,
)

from chromeis_sync.sync_engine.framework.identity_recovery.invoice_identity_resolver import (
    InvoiceIdentityResolver,
)

from chromeis_sync.sync_engine.framework.identity_recovery.repair_plan_builder import (
    RepairPlanBuilder,
)

from chromeis_sync.sync_engine.framework.identity_recovery.repair_strategy_resolver import (
    RepairStrategyResolver,
)


class RepairVerifier:

    @staticmethod
    def verify(invoice_id):

        plan = RepairPlanBuilder.build(
            invoice_id
        )

        if not plan["success"]:

            return {
                "success": False,
                "can_commit": False,
                "invoice": invoice_id,
                "errors": [
                    "Repair plan could not be generated."
                ],
                "warnings": [],
            }

        invoice = InvoiceIdentityResolver.get(
            plan["invoice"]
        )

        strategy = RepairStrategyResolver.resolve(
            invoice
        )

        checks = {
            "structure": RepairVerifier.verify_structure(
                plan,
                strategy,
            ),
            "identity": RepairVerifier.verify_identity(
                plan,
            ),
            "financial": RepairVerifier.verify_financial(
                plan,
            ),
            "business": RepairVerifier.verify_business(
                plan,
            ),
            "ledger": RepairVerifier.verify_ledger(
                plan,
            ),
            "references": RepairVerifier.verify_references(
                plan,
            ),
        }

        errors = []

        warnings = []

        for _, result in checks.items():

            if not result["success"]:

                errors.extend(
                    result["errors"]
                )

            warnings.extend(
                result["warnings"]
            )

        return {

            "success": len(errors) == 0,

            "can_commit": len(errors) == 0,

            "invoice": invoice_id,

            "checks": checks,

            "errors": errors,

            "warnings": warnings,

        }

    @staticmethod
    def verify_structure(
        plan,
        strategy,
    ):

        comparison = InvoiceComparator.compare(
            plan["invoice"]
        )

        errors = []

        warnings = []

        if not comparison.get(
            "erp_invoice"
        ):

            errors.append(
                "ERP invoice not found."
            )

            return {

                "success": False,

                "errors": errors,

                "warnings": warnings,

            }

        if (
            comparison["erp_rows"]
            != comparison["expected_rows"]
        ):

            if (
                strategy
                == RepairStrategyResolver.DRAFT_MUTATION
            ):

                errors.append(
                    f"ERP contains "
                    f"{comparison['erp_rows']} rows "
                    f"but reconstruction expects "
                    f"{comparison['expected_rows']}."
                )

            else:

                warnings.append(
                    f"ERP contains "
                    f"{comparison['erp_rows']} rows "
                    f"but reconstruction expects "
                    f"{comparison['expected_rows']}."
                )

        invoice = InvoiceIdentityResolver.get(
            plan["invoice"]
        )

        if (
            strategy
            == RepairStrategyResolver.DRAFT_MUTATION
            and invoice.docstatus != 0
        ):

            errors.append(
                f"Invoice is not Draft "
                f"(docstatus={invoice.docstatus})."
            )

        if getattr(
            invoice,
            "is_return",
            0,
        ):

            errors.append(
                "Return invoices are not supported."
            )

        if getattr(
            invoice,
            "amended_from",
            None,
        ):

            errors.append(
                "Amended invoices are not supported."
            )

        names = []

        for row in invoice.items:

            if row.name in names:

                errors.append(
                    f"Duplicate ERP row "
                    f"{row.name}."
                )

            names.append(
                row.name
            )

        expected_idx = 1

        for row in invoice.items:

            if row.idx != expected_idx:

                errors.append(
                    f"Invalid idx {row.idx}. "
                    f"Expected {expected_idx}."
                )

            expected_idx += 1

        for row in invoice.items:

            if not row.item_code:

                errors.append(
                    f"Row {row.idx} missing item_code."
                )

            if not row.income_account:

                errors.append(
                    f"Row {row.idx} missing income_account."
                )

            if row.qty is None:

                errors.append(
                    f"Row {row.idx} missing qty."
                )

            if row.rate is None:

                errors.append(
                    f"Row {row.idx} missing rate."
                )

            if row.amount is None:

                errors.append(
                    f"Row {row.idx} missing amount."
                )

        return {

            "success": len(errors) == 0,

            "errors": errors,

            "warnings": warnings,

        }

    @staticmethod
    def verify_identity(
        plan,
    ):

        return {
            "success": True,
            "errors": [],
            "warnings": [],
        }

    @staticmethod
    def verify_financial(
        plan,
    ):

        return {
            "success": True,
            "errors": [],
            "warnings": [],
        }

    @staticmethod
    def verify_business(
        plan,
    ):

        return {
            "success": True,
            "errors": [],
            "warnings": [],
        }

    @staticmethod
    def verify_ledger(
        plan,
    ):

        return {
            "success": True,
            "errors": [],
            "warnings": [],
        }

    @staticmethod
    def verify_references(
        plan,
    ):

        return {
            "success": True,
            "errors": [],
            "warnings": [],
        }
