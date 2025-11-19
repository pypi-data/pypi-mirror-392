class MineatarError(Exception):
    """Base class for all Mineatar exceptions."""

    pass


class InvalidUUIDError(MineatarError):
    """Raised when an invalid UUID is provided."""

    pass


class APIError(MineatarError):
    """Raised when there is an error with the Mineatar API."""

    pass


class RateLimitError(MineatarError):
    """Raised when the API rate limit is exceeded."""

    pass
