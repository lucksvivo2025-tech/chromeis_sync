from __future__ import annotations

import re


class DescriptionParser:
    """
    Performs generic text normalization.

    This parser does NOT determine business meaning.
    It only produces a canonical description that
    downstream parsers can consume.
    """

    _MULTISPACE = re.compile(r"\s+")
    _PUNCTUATION = re.compile(r"[:|,_\-]+")

    def normalize(
        self,
        description: str,
    ) -> str:

        if not description:
            return ""

        text = description.strip().lower()

        text = self._PUNCTUATION.sub(" ", text)

        text = self._MULTISPACE.sub(" ", text)

        return text.strip()
