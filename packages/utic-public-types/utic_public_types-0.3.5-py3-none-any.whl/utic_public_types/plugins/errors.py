"""Error classes for utic_types library.

These error classes are used for handling various provider and user errors
across different embedding and connector services.

All custom errors inherit from UnstructuredIngestError, making it easy to
distinguish internal errors from external Python exceptions.
"""


class UnstructuredIngestError(Exception):
    """Base exception for all Unstructured ingestion errors.

    All custom error classes should inherit from this base class.
    This allows easy identification of internal errors vs external exceptions.

    Attributes:
        status_code: Optional HTTP status code associated with this error type.
    """

    status_code: int | None = None


# Connection Errors
class UnstructuredConnectionError(UnstructuredIngestError):
    """Error connecting to a data source or service."""

    status_code: int | None = 400


class SourceConnectionError(UnstructuredConnectionError):
    """Error retrieving data from upstream data source."""

    status_code: int | None = 400


class SourceConnectionNetworkError(SourceConnectionError):
    """Network error connecting to upstream data source."""

    status_code: int | None = 400


class DestinationConnectionError(UnstructuredConnectionError):
    """Error connecting to downstream data destination."""

    status_code: int | None = 400


class EmbeddingEncoderConnectionError(UnstructuredConnectionError):
    """Error connecting to the embedding model provider."""

    status_code: int | None = 400


# User Errors
class UserError(UnstructuredIngestError):
    """Error caused by user input or configuration."""

    status_code: int | None = 401


class UserAuthError(UserError):
    """User authentication or authorization error."""

    status_code: int | None = 401


class RateLimitError(UserError):
    """Rate limit exceeded error."""

    status_code: int | None = 429


class QuotaError(UserError):
    """User quota exceeded error."""


# Provider Errors
class ProviderError(UnstructuredIngestError):
    """Error from an external service provider."""

    status_code: int | None = 500


# HTTP-style Errors
class NotFoundError(UnstructuredIngestError):
    """Requested resource not found."""

    status_code: int | None = 404


class UnstructuredTimeoutError(UnstructuredIngestError):
    """Operation timed out."""

    status_code: int | None = 408


class ResponseError(UnstructuredIngestError):
    """Invalid or unexpected response from a service."""

    status_code: int | None = 400


# Data Processing Errors
class WriteError(UnstructuredIngestError):
    """Error writing to downstream data destination."""

    status_code: int | None = 400


class PartitionError(UnstructuredIngestError):
    """Error partitioning content."""


class ValidationError(UnstructuredIngestError):
    """Data validation error."""


class MissingCategoryError(UnstructuredIngestError):
    """Required category is missing."""


# Type-related Errors (renamed to avoid shadowing builtins)
class UnstructuredValueError(UnstructuredIngestError):
    """Invalid value error (internal, not the builtin ValueError)."""


class UnstructuredKeyError(UnstructuredIngestError):
    """Key not found error (internal, not the builtin KeyError)."""


class UnstructuredTypeError(UnstructuredIngestError):
    """Type error (internal, not the builtin TypeError)."""


class UnstructuredFileExistsError(UnstructuredIngestError):
    """File already exists error (internal, not the builtin FileExistsError)."""


# Specialized Errors
class IcebergCommitFailedException(UnstructuredIngestError):
    """Failed to commit changes to an Iceberg table."""


def is_internal_error(e: Exception) -> bool:
    """Check if an exception is an internal Unstructured error.

    Args:
        e: The exception to check.

    Returns:
        True if the exception is an UnstructuredIngestError subclass,
        False otherwise (including Python builtin exceptions).

    Examples:
        >>> is_internal_error(UserError("test"))
        True
        >>> is_internal_error(ValueError("test"))
        False
    """
    return isinstance(e, UnstructuredIngestError)


__all__ = [
    # Base
    "UnstructuredIngestError",
    # Connection errors
    "UnstructuredConnectionError",
    "SourceConnectionError",
    "SourceConnectionNetworkError",
    "DestinationConnectionError",
    "EmbeddingEncoderConnectionError",
    # User errors
    "UserError",
    "UserAuthError",
    "RateLimitError",
    "QuotaError",
    # Provider errors
    "ProviderError",
    # HTTP-style errors
    "NotFoundError",
    "UnstructuredTimeoutError",
    "ResponseError",
    # Data processing errors
    "WriteError",
    "PartitionError",
    "ValidationError",
    "MissingCategoryError",
    # Type-related errors
    "UnstructuredValueError",
    "UnstructuredKeyError",
    "UnstructuredTypeError",
    "UnstructuredFileExistsError",
    # Specialized errors
    "IcebergCommitFailedException",
    # Utility function
    "is_internal_error",
]
