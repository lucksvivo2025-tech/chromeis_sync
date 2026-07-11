from __future__ import annotations

from decimal import Decimal

import frappe

from chromeis_sync.migration_audit.domain.models.whmcs import (
    WHMCSHeader,
    WHMCSInvoice,
    WHMCSItem,
)


class WHMCSProvider:
    """
    Reads WHMCS mirror database.

    No validation.
    No matching.
    No rebuilding.

    Pure data mapper.
    """

    def load_invoice(
        self,
        invoice_id: int,
    ) -> WHMCSInvoice:

        return WHMCSInvoice(
            header=self._load_header(invoice_id),
            items=self._load_items(invoice_id),
            taxes=[],
        )

    def _load_header(
        self,
        invoice_id: int,
    ) -> WHMCSHeader:

        rows = frappe.db.sql(
            """
            SELECT
                id,
                userid,
                status,
                date,
                duedate,
                subtotal,
                tax,
                tax2,
                credit,
                total,
                paymentmethod,
                notes
            FROM whmcs_mirror.tblinvoices
            WHERE id = %s
            LIMIT 1
            """,
            (invoice_id,),
            as_dict=True,
        )

        if not rows:
            raise ValueError(
                f"WHMCS Invoice {invoice_id} not found."
            )

        row = rows[0]

        return WHMCSHeader(
            invoice_id=row["id"],
            userid=row["userid"],
            status=row["status"],
            date=row["date"],
            due_date=row["duedate"],
            subtotal=Decimal(str(row["subtotal"])),
            tax=Decimal(str(row["tax"])),
            tax2=Decimal(str(row["tax2"])),
            credit=Decimal(str(row["credit"])),
            total=Decimal(str(row["total"])),
            payment_method=row["paymentmethod"],
            notes=row["notes"],
        )

    def _load_items(
        self,
        invoice_id: int,
    ) -> list[WHMCSItem]:

        rows = frappe.db.sql(
            """
            SELECT
                id,
                invoiceid,
                userid,
                type,
                relid,
                description,
                amount,
                taxed,
                duedate,
                paymentmethod,
                notes
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid = %s
            ORDER BY id
            """,
            (invoice_id,),
            as_dict=True,
        )

        items = []

        for row in rows:
            items.append(
                WHMCSItem(
                    id=row["id"],
                    invoice_id=row["invoiceid"],
                    user_id=row["userid"],
                    type=row["type"],
                    relid=row["relid"],
                    description=row["description"],
                    amount=Decimal(str(row["amount"])),
                    taxed=bool(row["taxed"]),
                    due_date=row["duedate"],
                    payment_method=row["paymentmethod"],
                    notes=row["notes"],
                )
            )

        return items
