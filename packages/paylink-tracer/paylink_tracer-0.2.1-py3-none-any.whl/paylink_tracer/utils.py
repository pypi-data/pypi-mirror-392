"""Utility functions for Paylink Tracer SDK."""

import json
import logging
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from paylink_tracer.constants import (
    API_ENDPOINT_PATH,
    DEFAULT_BASE_URL,
    HEADER_API_KEY,
    HEADER_PAYMENT_PROVIDER,
    HEADER_PROJECT_NAME,
    HEADER_TRACING_ENABLED,
    LOGGER_NAME,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(LOGGER_NAME)


def get_header_value(headers: Dict[str, str], header_name: str) -> Optional[str]:
    """Get header value from normalized headers.

    Args:
        headers: Dictionary of normalized headers (lowercase keys)
        header_name: Header name to look up

    Returns:
        Header value or None if not found
    """
    return headers.get(header_name)


def get_config_from_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Extract config from request headers.

    Args:
        headers: Dictionary of normalized headers (lowercase keys)

    Returns:
        Dictionary with api_key, project_name, payment_provider, enabled
    """
    tracing_value = get_header_value(headers, HEADER_TRACING_ENABLED)
    return {
        "api_key": get_header_value(headers, HEADER_API_KEY),
        "project_name": get_header_value(headers, HEADER_PROJECT_NAME),
        "payment_provider": get_header_value(headers, HEADER_PAYMENT_PROVIDER),
        "enabled": tracing_value.lower() == "enabled" if tracing_value else True,
    }


def get_runtime_info() -> Dict[str, str]:
    """Get runtime and environment information.

    Returns:
        Dictionary with sdk_version, runtime, os, host
    """
    return {
        "sdk_version": "0.2.1",
        "runtime": f"python-{sys.version_info.major}.{sys.version_info.minor}",
        "os": platform.system(),
        "host": platform.node(),
    }


def extract_response(result: Any) -> Any:
    """Extract response from result - simple extraction.

    Handles TextContent objects, JSON strings, and plain values.

    Args:
        result: The function result to extract

    Returns:
        Extracted and parsed result data
    """
    if isinstance(result, list) and len(result) > 0 and hasattr(result[0], "text"):
        # TextContent objects
        texts = [item.text for item in result if hasattr(item, "text")]
        if len(texts) == 1:
            try:
                return json.loads(texts[0])
            except (json.JSONDecodeError, TypeError):
                return texts[0]
        return texts
    elif isinstance(result, str):
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return result
    else:
        return result


def build_trace_payload(
    trace_id: str,
    request_id: str,
    tool_name: str,
    project_name: str,
    payment_provider: str,
    arguments: Dict[str, Any],
    response: Any,
    status: str,
    duration_ms: float,
    trace_ctx: Dict[str, Any],
    headers: Dict[str, str],
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Build trace payload dictionary.

    Args:
        trace_id: Unique trace ID
        request_id: Request ID
        tool_name: Name of the tool
        project_name: Project name
        payment_provider: Payment provider
        arguments: Tool arguments
        response: Tool response
        status: Trace status
        duration_ms: Duration in milliseconds
        trace_ctx: Trace context from contextvars
        headers: Request headers
        error: Optional error message

    Returns:
        Complete trace payload dictionary
    """
    request_data = trace_ctx.get("request", {})
    span_id = trace_id[:9] if len(trace_id) >= 9 else trace_id

    payload: Dict[str, Any] = {
        "trace_id": trace_id,
        "request_id": request_id,
        "tool_name": tool_name,
        "project_name": project_name,
        "payment_provider": payment_provider,
        "arguments": arguments,
        "response": response,
        "status": status,
        "duration_ms": duration_ms,
        "request_context": {
            "method": request_data.get("method"),
            "path": request_data.get("path"),
            "client": request_data.get("client", {}),
            "server": request_data.get("server", {}),
            "headers": headers,
        },
        "environment": {
            "mcp_protocol_version": trace_ctx.get("environment", {}).get("mcp_protocol_version"),
            **get_runtime_info(),
        },
        "meta": {
            "span_id": span_id,
            "parent_trace_id": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }

    if error:
        payload["error"] = error

    return payload


def send_trace_to_api(
    trace_data: Dict[str, Any],
    api_key: Optional[str] = None,
) -> None:
    """Send trace data to the API endpoint.

    Args:
        trace_data: Trace data to send
        api_key: Optional API key for authentication
    """
    # Use the final endpoint directly (with trailing slash) to avoid redirect
    endpoint = f"{DEFAULT_BASE_URL.rstrip('/')}{API_ENDPOINT_PATH}/"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(endpoint, json=trace_data, headers=headers)
            if response.status_code >= 400:
                logger.warning("Failed to send trace: HTTP %d", response.status_code)
    except Exception as e:
        logger.error("Error sending trace: %s", e, exc_info=True)

