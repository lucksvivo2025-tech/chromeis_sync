class SyncEngineError(Exception):
    """Base exception for the Sync Engine."""
    pass


class ConfigurationError(SyncEngineError):
    """Raised when sync configuration is invalid."""
    pass


class SnapshotError(SyncEngineError):
    """Raised when a snapshot cannot be created."""
    pass


class BuilderError(SyncEngineError):
    """Raised when document construction fails."""
    pass


class TransactionError(SyncEngineError):
    """Raised when a database transaction fails."""
    pass


class ApiError(SyncEngineError):
    """Raised when WHMCS API returns an error."""
    pass


class ValidationError(SyncEngineError):
    """Raised when validation fails."""
    pass


class PlannerError(SyncEngineError):
    """Raised when planning fails."""
    pass
