from __future__ import annotations

from abc import ABC, abstractmethod

from chromeis_sync.migration_audit.domain.parser_results.parser_result import (
    ParserResult,
)


class BaseResourceParser(ABC):
    """
    Base contract for all resource parsers.

    Every product family (Domain, VPS, SSL, Hosting...)
    implements this interface.
    """

    @abstractmethod
    def parse(
        self,
        text: str,
    ) -> ParserResult[str]:
        """
        Extract the business resource
        from normalized text.
        """
        raise NotImplementedError
