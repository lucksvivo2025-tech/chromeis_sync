import frappe
from chromeis_sync.migration_audit.classification import CommercialClassifier

class InvoiceRebuilder:

    HEADER_FIELDS = [
        "customer",
        "customer_name",
        "company",
        "posting_date",
        "posting_time",
        "set_posting_time",
        "due_date",
        "currency",
        "conversion_rate",
        "selling_price_list",
        "price_list_currency",
        "plc_conversion_rate",
        "debit_to",
        "cost_center",
        "remarks",
        "custom_whmcs_client_id",
        "whmcs_invoice_id",
        "update_outstanding_for_self",
    ]

    ITEM_FIELDS = [
        "item_code",
        "item_name",
        "description",
        "qty",
        "uom",
        "stock_uom",
        "conversion_factor",
        "rate",
        "income_account",
        "cost_center",
    ]
    def __init__(self, snapshot, target_currency):
        self.snapshot = snapshot
        self.target_currency = target_currency


    def resolve_whmcs_invoice_id(self):

        whmcs_id = self.snapshot["header"].get("whmcs_invoice_id")

        if whmcs_id:
            return int(whmcs_id)

        name = self.snapshot["header"]["name"]

        if name.startswith("ACC-SINV-WH-"):
            try:
                return int(name.replace("ACC-SINV-WH-", ""))
            except ValueError:
                pass

        return None


    def load_whmcs_items(self):

        whmcs_id = self.resolve_whmcs_invoice_id()

        if not whmcs_id:
            return []

        return frappe.db.sql("""
            SELECT *
            FROM whmcs_mirror.tblinvoiceitems
            WHERE invoiceid=%s
            ORDER BY id
        """, whmcs_id, as_dict=True)

    def load_whmcs_invoice(self):

        whmcs_id = self.resolve_whmcs_invoice_id()

        if not whmcs_id:
            return None

        rows = frappe.db.sql("""
            SELECT *
            FROM whmcs_mirror.tblinvoices
            WHERE id=%s
        """, whmcs_id, as_dict=True)

        if rows:
            return rows[0]

        return None

    def map_whmcs_item(self, row):

        item = {
            "qty": 1,
            "uom": "Unit",
            "stock_uom": "Unit",
            "conversion_factor": 1,
            "cost_center": "Main - CPL",
            "rate": float(row.get("amount") or 0),
            "description": row.get("description")
        }

        t = (row.get("type") or "").strip()
        desc = (row.get("description") or "").lower()

        # ----------------------------------------------------------
        # Normalize known WHMCS inconsistencies before mapping.
        #
        # WHMCS sometimes stores Domain Renewal / Registration /
        # Transfer invoice items with type='Hosting'.
        # The description is more reliable than the type.
        # ----------------------------------------------------------

        if desc.startswith("domain renewal"):
            t = "Domain"

        elif desc.startswith("domain registration"):
            t = "Domain"

        elif desc.startswith("domain transfer"):
            t = "Domain"

        elif "late fee" in desc:
            t = "LateFee"

        elif desc.startswith("addon ("):
            t = "Addon"

        if (
            t in ("Hosting", "PromoHosting", "Upgrade", "Setup")
            or (
                t == ""
                and (
                    "linux" in desc
                    or "windows" in desc
                    or "hosting" in desc
                    or "cpanel" in desc
                    or "plesk" in desc
                    or "vps" in desc
                    or "reseller" in desc
                    or "dedicated" in desc
                )
            )
        ):
            item["item_code"] = "Hosting Service"
            item["item_name"] = "Hosting Service"
            item["income_account"] = "Sales - Shared Hosting - CPL"

        elif (
            t in (
                "Domain",
                "DomainRegister",
                "DomainTransfer",
                "DomainRedemptionFee",
                "PromoDomain"
            )
            or (t == "" and "domain" in desc)
        ):
            item["item_code"] = "Domain Registration"
            item["item_name"] = "Domain Registration"
            item["income_account"] = "Sales - Domain and SSL Services - CPL"

        elif t == "Addon":

            # Hosting-related addons (Advance/CPanel, backups, etc.)
            if (
                "cpanel" in desc
                or "plesk" in desc
                or "backup" in desc
                or "advance/" in desc
                or "advance\\" in desc
                or desc.startswith("advance/")
                or desc.startswith("advance\\")
            ):
                item["item_code"] = "Hosting Service"
                item["item_name"] = "Hosting Service"
                item["income_account"] = "Sales - Managed and Professional Services - CPL"

            # SSL and other domain-related addons
            else:
                item["item_code"] = "Service Addon"
                item["item_name"] = "Service Addon"
                item["income_account"] = "Sales - Domain and SSL Services - CPL"

        elif t == "LateFee":

            if (
                desc.startswith("late fee")
                or desc.startswith("reversal of late fee")
                or desc.startswith("late fee reversal")
            ):
                item["item_code"] = "Late Fee"
                item["item_name"] = "Late Fee"
                item["income_account"] = "Late Fee Income - CPL"

            else:
                item["item_code"] = "Hosting Service"
                item["item_name"] = "Hosting Service"
                item["income_account"] = "Sales - Managed and Professional Services - CPL"

        elif t == "AddFunds":
            item["item_code"] = "Customer Deposit"
            item["item_name"] = "Customer Deposit"
            item["income_account"] = "Customer Deposits - CPL"

        elif t == "Invoice":
            item["item_code"] = "Invoice Adjustment"
            item["item_name"] = "Invoice Adjustment"
            item["income_account"] = "Sales - Shared Hosting - CPL"

        elif t == "Item":
            item["item_code"] = "Professional Service"
            item["item_name"] = "Professional Service"
            item["income_account"] = "Sales - Professional Services - CPL"

        elif t == "GroupDiscount":
            item["item_code"] = "Discount"
            item["item_name"] = "Discount"
            item["income_account"] = "Sales - Shared Hosting - CPL"

        elif t in ("DomainAddonDNS", "DomainAddonEMF"):
            item["item_code"] = "Domain Registration"
            item["item_name"] = "Domain Registration"
            item["income_account"] = "Sales - Domain and SSL Services - CPL"

        elif t == "Addon":
            item["item_code"] = "Service Addon"
            item["item_name"] = "Service Addon"

        else:
            item["item_code"] = "Hosting Service"
            item["item_name"] = "Hosting Service"
            item["income_account"] = "Sales - Shared Hosting - CPL"

        return item

    def build(self):

        old = self.snapshot["header"]

        inv = frappe.new_doc("Sales Invoice")

        # -------------------------
        # Header
        # -------------------------

        for field in self.HEADER_FIELDS:
            if field in old:
                inv.set(field, old[field])

        # Preserve historical posting date/time during migration
        inv.set_posting_time = 1

        inv.currency = self.target_currency

        # Preserve historical currency metadata
        inv.conversion_rate = old.get("conversion_rate") or 1

        inv.price_list_currency = (
            old.get("price_list_currency")
            or self.target_currency
        )

        inv.plc_conversion_rate = (
            old.get("plc_conversion_rate")
            or 1
        )

        # -------------------------
        # Items
        # -------------------------

        whmcs_items = self.load_whmcs_items()
        whmcs_invoice = self.load_whmcs_invoice()

        single_item = (
            whmcs_invoice is not None
            and len(whmcs_items) == 1
        )

        if whmcs_items:

            for index, row in enumerate(whmcs_items):

                mapped_item = CommercialClassifier.map_whmcs_item(row)

                item = {}

                snapshot_item = None

                for candidate in self.snapshot["items"]:
                    if (
                        (candidate.get("description") or "").strip()
                        == (mapped_item.get("description") or "").strip()
                    ):
                        snapshot_item = candidate
                        break

                if snapshot_item:

                    # Existing ERP Snapshot
                    if "parenttype" in snapshot_item:

                        # Preserve only ERP-specific values
                        for field in (
                            "qty",
                            "uom",
                            "stock_uom",
                            "conversion_factor",
                            "cost_center",
                        ):
                            if field in snapshot_item:
                                item[field] = snapshot_item[field]

                        # Always use WHMCS commercial classification
                        item["item_code"] = mapped_item["item_code"]
                        item["item_name"] = mapped_item["item_name"]
                        item["income_account"] = mapped_item["income_account"]

                    # Missing Invoice Snapshot
                    else:

                        for field in (
                            "item_code",
                            "item_name",
                            "income_account",
                            "cost_center",
                            "qty",
                            "uom",
                            "stock_uom",
                            "conversion_factor",
                        ):
                            item[field] = mapped_item[field]

                # Commercial values always come from WHMCS
                item["description"] = mapped_item.get("description")
                item["rate"] = mapped_item.get("rate")
                item["amount"] = mapped_item.get("amount")

                invoice_credit = abs(float(whmcs_invoice.get("credit") or 0))

                # Preserve the original WHMCS item values.
                # Taxes are migrated separately.

                inv.append("items", item)

        else:

            # Fallback for invoices not available in WHMCS
            for row in self.snapshot["items"]:

                item = {}

                for field in self.ITEM_FIELDS:
                    if field in row:
                        item[field] = row[field]

                inv.append("items", item)

                whmcs_invoice["tax"]
                whmcs_invoice["tax2"]

        # -------------------------
        # Historical WHMCS Taxes
        # -------------------------

        print(f"DEBUG: WHMCS Invoice={whmcs_invoice}")

        if whmcs_invoice:

            for tax_value in (
                float(whmcs_invoice.get("tax") or 0),
                float(whmcs_invoice.get("tax2") or 0),
            ):

                print(f"DEBUG: Tax Value={tax_value}")

                if tax_value <= 0:
                    continue

                tax = inv.append("taxes", {})

                print("DEBUG: Tax row appended")

                tax.charge_type = "Actual"
                tax.account_head = "GST - CPL"
                tax.description = "WHMCS Historical Tax"
                tax.cost_center = "Main - CPL"
                tax.rate = 0
                tax.tax_amount = tax_value

        # IMPORTANT:
        # Do NOT insert or submit here.
        # The transaction controls database writes.

        return inv
