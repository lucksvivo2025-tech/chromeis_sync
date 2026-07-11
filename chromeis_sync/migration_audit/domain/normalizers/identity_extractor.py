from __future__ import annotations

from chromeis_sync.migration_audit.domain.classifiers.service_type_resolver import (
    ServiceTypeResolver,
)
from chromeis_sync.migration_audit.domain.parsers.description_parser import (
    DescriptionParser,
)
from chromeis_sync.migration_audit.domain.parsers.operation_parser import (
    OperationParser,
)
from chromeis_sync.migration_audit.domain.registry.resource_parser_registry import (
    ResourceParserRegistry,
)
from chromeis_sync.migration_audit.domain.value_objects.business_identity import (
    BusinessIdentity,
)


class IdentityExtractor:
    """
    Coordinates all domain parsers to build
    a BusinessIdentity.
    """

    def __init__(self):

        self.description_parser = DescriptionParser()

        self.operation_parser = OperationParser()

        self.service_resolver = ServiceTypeResolver()

        self.resource_registry = ResourceParserRegistry()

    def extract(
        self,
        description: str,
    ) -> BusinessIdentity:

        normalized = self.description_parser.normalize(description)

        operation = self.operation_parser.parse(normalized)

        service_type = self.service_resolver.resolve(normalized)

        parser = self.resource_registry.get(service_type)

        resource = None

        if parser:

            resource = parser.parse(normalized).value

        return BusinessIdentity(

            service_type=service_type,

            operation=operation,

            resource_name=resource,

            billing_cycle=None,

            period_start=None,

            period_end=None,

            amount_signature=None,

        )
