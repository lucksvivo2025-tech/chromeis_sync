class LegacyInvoiceClassifier:

    DOMAIN_KEYWORDS = [
        "registration",
        "domain registration",
        "domain renewal",
        "renewal of",
        ".com",
        ".net",
        ".org",
        ".pk",
        ".co.uk",
        ".tv",
        ".today",
    ]

    HOSTING_KEYWORDS = [
        "hosting",
        "cpanel",
        "plesk",
        "linux",
        "windows",
        "cloud",
        "vps",
        "dedicated",
        "server",
        "package",
        "reseller",
        "shared",
        "wordpress",
    ]

    @classmethod
    def classify(cls, item):

        item_type = (item.get("type") or "").strip()

        #
        # Modern WHMCS item types
        #

        if item_type:

            if item_type in (
                "Hosting",
                "PromoHosting",
            ):
                return "Hosting"

            if item_type in (
                "Domain",
                "DomainRegister",
                "DomainTransfer",
            ):
                return "Domain"

            if item_type == "Addon":
                return "Addon"

            return None

        #
        # Legacy blank invoice items
        #

        description = (
            item.get("description") or ""
        ).lower()

        #
        # Hosting FIRST
        #

        for keyword in cls.HOSTING_KEYWORDS:
            if keyword in description:
                return "Hosting"

        #
        # Domain SECOND
        #

        for keyword in cls.DOMAIN_KEYWORDS:
            if keyword in description:
                return "Domain"

        return None
