"""
Paylink Tracer SDK - Production-grade tracing for payment operations.

This SDK provides a decorator-based tracing solution that automatically
captures and sends payment tool execution data to your Paylink API endpoint.

Example:
    >>> from paylink_tracer import paylink_tracer, set_trace_context_provider
    >>> import contextvars
    >>>
    >>> trace_context = contextvars.ContextVar("trace_context")
    >>> set_trace_context_provider(trace_context)
    >>>
    >>> @paylink_tracer()
    ... async def call_tool(name: str, arguments: dict):
    ...     return result
"""

from paylink_tracer.exceptions import (
    PaylinkTracerAPIError,
    PaylinkTracerConfigurationError,
    PaylinkTracerError,
    PaylinkTracerValidationError,
)
from paylink_tracer.tracer import (
    paylink_tracer,
    set_trace_context_provider,
)

__version__ = "0.2.1"
__all__ = [
    # Main decorator
    "paylink_tracer",
    "set_trace_context_provider",
    # Exceptions
    "PaylinkTracerError",
    "PaylinkTracerConfigurationError",
    "PaylinkTracerAPIError",
    "PaylinkTracerValidationError",
]
