"""Custom exceptions for Paylink Tracer SDK."""


class PaylinkTracerError(Exception):
    """Base exception for Paylink Tracer SDK."""

    pass


class PaylinkTracerConfigurationError(PaylinkTracerError):
    """Raised when there's a configuration error."""

    pass


class PaylinkTracerAPIError(PaylinkTracerError):
    """Raised when there's an error communicating with the API."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class PaylinkTracerValidationError(PaylinkTracerError):
    """Raised when input validation fails."""

    pass

