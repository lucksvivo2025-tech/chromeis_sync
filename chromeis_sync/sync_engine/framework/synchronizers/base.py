class BaseSynchronizer:
    """
    Base class for all synchronizers.

    Every entity synchronizer should inherit from this class.
    """

    entity = None

    @classmethod
    def synchronize(cls, identifier):
        """
        Synchronize one WHMCS record.

        Child synchronizers will override this method.
        """

        return {
            "entity": cls.entity,
            "identifier": str(identifier),
            "status": "NOT_IMPLEMENTED",
        }
