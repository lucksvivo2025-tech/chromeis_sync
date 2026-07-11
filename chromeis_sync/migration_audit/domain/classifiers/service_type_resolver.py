from __future__ import annotations

from chromeis_sync.migration_audit.domain.enums.service_type import (
    ServiceType,
)


class ServiceTypeResolver:
    """
    Resolves the business product/service type
    from a normalized invoice description.

    This class contains deterministic business rules.
    """

    RULES = {
        ServiceType.DOMAIN: (
            "domain",
            ".com",
            ".net",
            ".org",
            ".pk",
        ),

        ServiceType.HOSTING: (
            "hosting",
            "cpanel",
            "plesk",
            "shared hosting",
            "reseller",
        ),

        ServiceType.VPS: (
            "vps",
            "virtual private server",
        ),

        ServiceType.DEDICATED: (
            "dedicated",
            "bare metal",
        ),

        ServiceType.SSL: (
            "ssl",
            "certificate",
        ),

        ServiceType.EMAIL: (
            "email",
            "exchange",
            "workspace",
            "microsoft 365",
        ),

        ServiceType.LICENSE: (
            "license",
            "licence",
            "whmcs",
            "cpanel license",
        ),
    }

    def resolve(
        self,
        text: str,
    ) -> ServiceType:

        text = text.lower()

        for service_type, keywords in self.RULES.items():
            for keyword in keywords:
                if keyword in text:
                    return service_type

        return ServiceType.UNKNOWN
