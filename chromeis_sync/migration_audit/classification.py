class CommercialClassifier:

    @staticmethod
    def map_whmcs_item(row):

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
