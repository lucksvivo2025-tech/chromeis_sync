from __future__ import annotations

import re


class DescriptionNormalizer:
    """
    Produces a canonical representation
    of invoice item descriptions.

    This class performs NO matching.
    It only normalizes text.
    """

    def normalize(
        self,
        description: str,
    ) -> str:
        raise NotImplementedError
