from chromeis_sync.sync_engine.framework.classification.business_matcher import (
    BusinessMatcher,
)

from chromeis_sync.sync_engine.framework.classification.legacy_invoice_classifier import (
    LegacyInvoiceClassifier,
)


class BusinessMapper:

    DEFAULT_INCOME_ACCOUNT = "Sales - Shared Hosting - CPL"

    MAP = {

        "Hosting": {
            "item_code": "Hosting Service",
            "item_name": "Hosting Service",
            "income_account": "Sales - Shared Hosting - CPL",
        },

        "Domain": {
            "item_code": "Domain Registration",
            "item_name": "Domain Registration",
            "income_account": "Sales - Domains - CPL",
        },

        "Addon": {
            "item_code": "Hosting Addon",
            "item_name": "Hosting Addon",
            "income_account": "Sales - Hosting Addons - CPL",
        },
    }

    @classmethod
    def map(cls, whmcs_item):

        #
        # First try the Business Matcher
        #

        catalog = BusinessMatcher.match(
            whmcs_item.get("description")
        )

        if catalog:

            mapping = dict(catalog)

            mapping["description"] = (
                whmcs_item.get("description") or ""
            ).strip()

            mapping["amount"] = float(
                whmcs_item.get("amount") or 0
            )

            mapping["qty"] = 1

            mapping["rate"] = mapping["amount"]

        else:

            family = LegacyInvoiceClassifier.classify(
                whmcs_item
            )

            if not family:
                return None

            mapping = dict(
                cls.MAP[family]
            )

            mapping["family"] = family

            mapping["description"] = (
                whmcs_item.get("description") or ""
            ).strip()

            mapping["amount"] = float(
                whmcs_item.get("amount") or 0
            )

            mapping["qty"] = 1

            mapping["rate"] = mapping["amount"]

        #
        # Legacy WHMCS identifiers
        #

        mapping["custom_whmcs_service_id"] = None
        mapping["custom_whmcs_domain_id"] = None
        mapping["custom_whmcs_addon_id"] = None

        relid = whmcs_item.get("relid")

        if relid:

            if mapping["family"] == "Hosting":

                mapping["custom_whmcs_service_id"] = relid

            elif mapping["family"] == "Domain":

                mapping["custom_whmcs_domain_id"] = relid

            elif mapping["family"] in (
                "Addon",
                "Backup",
                "Security",
                "Network",
            ):

                mapping["custom_whmcs_addon_id"] = relid

        return mapping
