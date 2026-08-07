from decimal import Decimal

import frappe

from chromeis_sync.migration_audit.domain.models.snapshot import (
    SnapshotHeader,
    SnapshotInvoice,
    SnapshotItem,
)


class WHMCSSnapshotProvider:

    @staticmethod
    def load(invoice_id):

        invoice = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
            """,
            (invoice_id,),
            as_dict=True,
        )

        if not invoice:
            return None

        invoice = invoice[0]

        items = frappe.db.sql(
            """
            SELECT *
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
            """,
            (invoice_id,),
            as_dict=True,
        )

        header = SnapshotHeader(

            invoice_name=str(invoice["id"]),

            customer=str(invoice["userid"]),
            customer_name=str(invoice["userid"]),

            company="WHMCS",

            currency="USD",

            posting_date=invoice["date"],
            posting_time=None,
            due_date=invoice["duedate"],

            whmcs_invoice_id=invoice["id"],
            custom_whmcs_client_id=invoice["userid"],

            remarks=invoice.get("notes"),

            grand_total=Decimal(str(invoice["total"])),
            net_total=Decimal(str(invoice["subtotal"])),
            rounded_total=Decimal(str(invoice["total"])),

            # Outstanding will later come from payment reconciliation.
            outstanding_amount=Decimal(str(invoice["total"])),

            cost_center=None,
        )

        snapshot_items = []

        for idx, row in enumerate(items, start=1):

            snapshot_items.append(

                SnapshotItem(

                    idx=idx,

                    item_code=(row.get("type") or "").strip(),
                    item_name=(row.get("type") or "").strip(),

                    description=(
                        row.get("description") or ""
                    ).strip(),

                    qty=Decimal("1"),

                    rate=Decimal(str(row.get("amount") or 0)),
                    amount=Decimal(str(row.get("amount") or 0)),

                    income_account=None,
                    cost_center=None,

                    warehouse=None,
                    project=None,

                    custom_whmcs_service_id=(
                        int(row["relid"])
                        if row.get("type") == "Hosting"
                        else None
                    ),

                    custom_whmcs_domain_id=(
                        int(row["relid"])
                        if row.get("type") in (
                            "Domain",
                            "DomainRegister",
                            "DomainTransfer",
                        )
                        else None
                    ),

                    custom_whmcs_addon_id=(
                        int(row["relid"])
                        if row.get("type") == "Addon"
                        else None
                    ),

                    custom_whmcs_config_id=None,

                )

            )

        return SnapshotInvoice(
            header=header,
            items=snapshot_items,
            taxes=[],
            gl_entries=[],
            created_at=invoice.get("created_at"),
        )
