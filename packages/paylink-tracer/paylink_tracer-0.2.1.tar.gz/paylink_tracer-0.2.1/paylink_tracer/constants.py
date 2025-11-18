"""Constants for Paylink Tracer SDK."""

# API Configuration
DEFAULT_BASE_URL = "https://backend.paylinkai.app"
API_ENDPOINT_PATH = "/api/v1/trace"
REQUEST_TIMEOUT = 10.0

# Environment Variable Names
ENV_API_KEY = "PAYLINK_API_KEY"
ENV_PROJECT_NAME = "PAYLINK_PROJECT"
ENV_PAYMENT_PROVIDER = "PAYMENT_PROVIDER"
ENV_TRACING_ENABLED = "PAYLINK_TRACING"

# Request Header Names (normalized to lowercase)
HEADER_API_KEY = "paylink-api-key"
HEADER_PROJECT_NAME = "paylink-project"
HEADER_PAYMENT_PROVIDER = "payment-provider"
HEADER_TRACING_ENABLED = "paylink-tracing"

# Trace Status Values
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"

# Error Keywords for Status Detection
ERROR_KEYWORDS = ["error", "failed", "failure", "exception"]
SUCCESS_KEYWORDS = ["success", "accepted", "completed"]

# Default Values
DEFAULT_PAYMENT_PROVIDER = "mpesa"
DEFAULT_PROJECT_NAME = "unknown"
DEFAULT_TRACING_ENABLED = True

# Logger Name
LOGGER_NAME = "paylink_tracer"

