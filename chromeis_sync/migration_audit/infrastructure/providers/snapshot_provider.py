from __future__ import annotations

from decimal import Decimal

import frappe

from chromeis_sync.migration_audit.domain.models.snapshot import (
    SnapshotInvoice,
    SnapshotHeader,
    SnapshotItem,
    SnapshotTax,
    SnapshotGLEntry,
)


class SnapshotProvider:
    """
    Loads a historical ERPNext Sales Invoice
    into immutable domain models.

    This class performs NO validation,
    NO rebuilding,
    NO business logic.

    It only reads ERPNext data.
    """

    def load(
        self,
        invoice_name: str,
    ) -> SnapshotInvoice:

        doc = frappe.get_doc("Sales Invoice", invoice_name)

        return SnapshotInvoice(
            header=self._load_header(doc),
            items=self._load_items(doc),
            taxes=self._load_taxes(doc),
            gl_entries=self._load_gl_entries(invoice_name),
        )

    def _load_header(
        self,
        doc,
    ) -> SnapshotHeader:

        return SnapshotHeader(

            invoice_name=doc.name,

            customer=doc.customer,
            customer_name=doc.customer_name,

            company=doc.company,
            currency=doc.currency,

            posting_date=doc.posting_date,
            posting_time=doc.posting_time,
            due_date=doc.due_date,

            whmcs_invoice_id=int(doc.whmcs_invoice_id)
            if doc.whmcs_invoice_id
            else None,

            custom_whmcs_client_id=int(doc.custom_whmcs_client_id)
            if doc.custom_whmcs_client_id
            else None,

            remarks=doc.remarks,

            grand_total=Decimal(str(doc.grand_total)),
            net_total=Decimal(str(doc.net_total)),
            rounded_total=Decimal(str(doc.rounded_total)),
            outstanding_amount=Decimal(str(doc.outstanding_amount)),

            cost_center=doc.cost_center,
        )

    def _load_items(
        self,
        doc,
    ) -> list[SnapshotItem]:

        items = []

        for row in doc.items:

            items.append(

                SnapshotItem(

                    idx=row.idx,

                    item_code=row.item_code,
                    item_name=row.item_name,
                    description=row.description,

                    qty=Decimal(str(row.qty)),
                    rate=Decimal(str(row.rate)),
                    amount=Decimal(str(row.amount)),

                    income_account=row.income_account,
                    cost_center=row.cost_center,

                    warehouse=row.warehouse,
                    project=row.project,

                    custom_whmcs_service_id=row.custom_whmcs_service_id,
                    custom_whmcs_domain_id=row.custom_whmcs_domain_id,
                    custom_whmcs_addon_id=row.custom_whmcs_addon_id,
                    custom_whmcs_config_id=row.custom_whmcs_config_id,

                )

            )

        return items

    def _load_taxes(
        self,
        doc,
    ) -> list[SnapshotTax]:

        taxes = []

        for row in doc.taxes:

            taxes.append(

                SnapshotTax(

                    idx=row.idx,

                    account_head=row.account_head,
                    charge_type=row.charge_type,

                    rate=Decimal(str(row.rate)),
                    tax_amount=Decimal(str(row.tax_amount)),

                    description=row.description,

                )

            )

        return taxes

    def _load_gl_entries(
        self,
        invoice_name: str,
    ) -> list[SnapshotGLEntry]:

        rows = frappe.get_all(
            "GL Entry",
            filters={
                "voucher_type": "Sales Invoice",
                "voucher_no": invoice_name,
            },
            fields=[
                "account",
                "debit",
                "credit",
                "cost_center",
                "against",
                "remarks",
            ],
            order_by="creation asc",
        )

    def list_migrated_invoices(
        self,
    ) -> list[tuple[int, str]]:
        """
        Returns:
            [
                (627, "ACC-SINV-WH-627"),
                (628, "ACC-SINV-WH-628"),
                ...
            ]
        """

        rows = frappe.get_all(
            "Sales Invoice",
            filters={
                "whmcs_invoice_id": ["is", "set"],
            },
            fields=[
                "name",
                "whmcs_invoice_id",
            ],
            order_by="whmcs_invoice_id asc",
        )

        return [
            (
                int(row.whmcs_invoice_id),
                row.name,
            )
            for row in rows
        ]

        entries = []

        for row in rows:

            entries.append(

                SnapshotGLEntry(

                    account=row.account,

                    debit=Decimal(str(row.debit)),
                    credit=Decimal(str(row.credit)),

                    cost_center=row.cost_center,
                    against=row.against,
                    remarks=row.remarks,

                )

            )

        return entries
