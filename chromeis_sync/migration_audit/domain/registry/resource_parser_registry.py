from __future__ import annotations

from chromeis_sync.migration_audit.domain.enums.service_type import (
    ServiceType,
)

from chromeis_sync.migration_audit.domain.parsers.resource.base_resource_parser import (
    BaseResourceParser,
)

from chromeis_sync.migration_audit.domain.parsers.resource.domain_resource_parser import (
    DomainResourceParser,
)


class ResourceParserRegistry:
    """
    Registry of resource parsers.

    Maps ServiceType -> Resource Parser.
    """

    def __init__(self) -> None:

        self._parsers: dict[
            ServiceType,
            BaseResourceParser,
        ] = {

            ServiceType.DOMAIN: DomainResourceParser(),

        }

    def get(
        self,
        service_type: ServiceType,
    ) -> BaseResourceParser | None:

        return self._parsers.get(service_type)
