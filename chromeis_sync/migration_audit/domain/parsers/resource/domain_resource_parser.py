from __future__ import annotations

import re

from chromeis_sync.migration_audit.domain.parser_results.parser_result import (
    ParserResult,
)

from chromeis_sync.migration_audit.domain.parsers.resource.base_resource_parser import (
    BaseResourceParser,
)


class DomainResourceParser(BaseResourceParser):
    """
    Extracts domain names from normalized invoice descriptions.
    """

    DOMAIN_PATTERN = re.compile(
        r"\b([a-z0-9][a-z0-9\-]*\.(?:com|net|org|pk|info|biz|co|io|ai|app|dev))\b",
        re.IGNORECASE,
    )

    def parse(
        self,
        text: str,
    ) -> ParserResult[str]:

        match = self.DOMAIN_PATTERN.search(text)

        if match:

            domain = match.group(1).lower()

            return ParserResult(
                value=domain,
                confidence=1.0,
                strategy="regex-domain",
                matched_text=domain,
            )

        return ParserResult(
            value=None,
            confidence=0.0,
            strategy="regex-domain",
            matched_text=None,
        )
