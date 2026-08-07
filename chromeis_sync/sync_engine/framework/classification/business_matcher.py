from chromeis_sync.sync_engine.framework.classification.business_catalog import (
    BusinessCatalog,
)


class BusinessMatcher:

    PRIMARY_SCORE = 10
    SECONDARY_SCORE = 2

    @classmethod
    def match(cls, description):

        text = (description or "").lower()

        best_match = None
        best_score = 0

        for product in BusinessCatalog.CATALOG:

            score = 0

            #
            # Primary keywords
            #

            for keyword in product.get("primary_keywords", []):

                if keyword.lower() in text:

                    score += cls.PRIMARY_SCORE

            #
            # Secondary keywords
            #

            for keyword in product.get("secondary_keywords", []):

                if keyword.lower() in text:

                    score += cls.SECONDARY_SCORE

            if score > best_score:

                best_score = score
                best_match = product

        if not best_match:

            return None

        result = dict(best_match)

        result["score"] = best_score

        return result
