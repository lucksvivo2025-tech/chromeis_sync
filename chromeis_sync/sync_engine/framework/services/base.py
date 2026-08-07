class BaseService:
    """
    Base business service.

    Coordinates:
        • Builder
        • Upsert
        • Validation

    Child services implement synchronize().
    """

    @classmethod
    def synchronize(cls, identifier):
        raise NotImplementedError

