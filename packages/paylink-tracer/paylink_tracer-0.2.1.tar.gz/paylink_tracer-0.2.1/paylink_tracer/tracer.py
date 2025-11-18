"""Paylink Tracer SDK - Simple tracing for payment operations."""

import contextvars
import logging
import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from paylink_tracer.constants import LOGGER_NAME
from paylink_tracer.utils import (
    build_trace_payload,
    extract_response,
    get_config_from_headers,
    send_trace_to_api,
)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])

# Configure logger
logger = logging.getLogger(LOGGER_NAME)

# Global reference to trace_context ContextVar
_trace_context_var: Optional[contextvars.ContextVar] = None


def set_trace_context_provider(trace_context: contextvars.ContextVar) -> None:
    """Set the trace context ContextVar to read from request headers.

    Args:
        trace_context: The ContextVar instance that holds trace context data
    """
    global _trace_context_var
    _trace_context_var = trace_context
    logger.debug("Trace context provider registered")


def _get_trace_context() -> Optional[Dict[str, Any]]:
    """Get trace context from contextvars if available."""
    if _trace_context_var is None:
        return None

    try:
        ctx = _trace_context_var.get(None)
        if ctx is not None and isinstance(ctx, dict):
            return ctx
        return None
    except (LookupError, ValueError, RuntimeError):
        return None








def paylink_tracer(func: Optional[F] = None) -> Union[Callable[[F], F], F]:
    """Decorator to automatically trace payment tool calls.

    Automatically reads configuration from request headers via trace_context.

    Example:
        >>> @paylink_tracer()
        ... async def call_tool(name: str, arguments: dict):
        ...     return result
    """

    def decorator(f: F) -> F:
        @wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get trace context
            trace_ctx = _get_trace_context()
            if not trace_ctx:
                # No trace context, skip tracing
                return await f(*args, **kwargs)

            # Get headers from trace context
            request_data = trace_ctx.get("request", {})
            headers = request_data.get("headers", {})
            if not headers:
                return await f(*args, **kwargs)

            # Get config from headers
            config = get_config_from_headers(headers)
            api_key = config.get("api_key")
            project_name = config.get("project_name")
            payment_provider = config.get("payment_provider", "mpesa")
            enabled = config.get("enabled", True)

            # Check if tracing is enabled
            if not enabled or not api_key or not project_name:
                return await f(*args, **kwargs)

            # Start timing
            start_time = time.time()

            # Get tool info
            tool_name = kwargs.get("name") or (args[0] if args else "unknown")
            arguments = kwargs.get("arguments") or (args[1] if len(args) > 1 else {})

            # Generate IDs
            trace_id = str(uuid.uuid4())
            request_id = kwargs.get("request_id") or f"req_{uuid.uuid4().hex[:10]}"

            # Call function
            status = "success"
            result = None
            error = None

            try:
                result = await f(*args, **kwargs)
            except Exception as e:
                status = "error"
                error = str(e)
                raise
            finally:
                # Calculate duration
                duration_ms = round((time.time() - start_time) * 1000, 2)

                # Extract response first
                response = extract_response(result) if result is not None else {}

                # Determine status from response - simple: just get status from response dict
                if status == "success" and isinstance(response, dict):
                    response_status = response.get("status", "").lower()
                    if response_status in ["success", "error", "failed", "failure"]:
                        status = response_status

                # Build trace payload
                trace_payload = build_trace_payload(
                    trace_id=trace_id,
                    request_id=request_id,
                    tool_name=tool_name,
                    project_name=project_name,
                    payment_provider=payment_provider,
                    arguments=arguments,
                    response=response,
                    status=status,
                    duration_ms=duration_ms,
                    trace_ctx=trace_ctx,
                    headers=headers,
                    error=error,
                )

                # Send trace
                send_trace_to_api(trace_payload, api_key)

            return result

        return wrapper  # type: ignore

    if func is None:
        return decorator
    else:
        return decorator(func)
