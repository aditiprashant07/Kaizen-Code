"""
shared/constants.py
===================
Single source of truth for all constants across api, engine, and ml layers.

Usage:
    from shared.constants import ErrorCode, ScoreThreshold, ConfigKey, HttpStatus

Rules:
    - Never hardcode values that appear here elsewhere in the codebase.
    - All values are immutable (use Enum or Final).
    - Sensitive config values (secrets, keys) must NEVER be stored here;
      use environment variables and reference their key names via ConfigKey only.
"""

from enum import Enum, unique
from typing import Final


# ---------------------------------------------------------------------------
# HTTP Status Codes
# ---------------------------------------------------------------------------

class HttpStatus(int, Enum):
    """Standard HTTP status codes used across the API layer."""
    OK                  = 200
    CREATED             = 201
    NO_CONTENT          = 204
    BAD_REQUEST         = 400
    UNAUTHORIZED        = 401
    FORBIDDEN           = 403
    NOT_FOUND           = 404
    CONFLICT            = 409
    UNPROCESSABLE       = 422
    TOO_MANY_REQUESTS   = 429
    INTERNAL_ERROR      = 500
    SERVICE_UNAVAILABLE = 503


# ---------------------------------------------------------------------------
# Application Error Codes
# ---------------------------------------------------------------------------

@unique
class ErrorCode(str, Enum):
    """
    Structured error codes returned in API responses.
    Format: DOMAIN_DESCRIPTION
    Domains: AUTH, INPUT, ANALYSIS, ML, ENGINE, SYSTEM
    """

    # Auth
    AUTH_INVALID_TOKEN          = "AUTH_INVALID_TOKEN"
    AUTH_TOKEN_EXPIRED          = "AUTH_TOKEN_EXPIRED"
    AUTH_INSUFFICIENT_SCOPE     = "AUTH_INSUFFICIENT_SCOPE"
    AUTH_USER_NOT_FOUND         = "AUTH_USER_NOT_FOUND"

    # Input validation
    INPUT_MISSING_FIELD         = "INPUT_MISSING_FIELD"
    INPUT_INVALID_TYPE          = "INPUT_INVALID_TYPE"
    INPUT_OUT_OF_RANGE          = "INPUT_OUT_OF_RANGE"
    INPUT_UNSUPPORTED_LANGUAGE  = "INPUT_UNSUPPORTED_LANGUAGE"
    INPUT_FILE_TOO_LARGE        = "INPUT_FILE_TOO_LARGE"
    INPUT_EMPTY_PAYLOAD         = "INPUT_EMPTY_PAYLOAD"

    # Code analysis (engine)
    ANALYSIS_PARSE_FAILED       = "ANALYSIS_PARSE_FAILED"
    ANALYSIS_TIMEOUT            = "ANALYSIS_TIMEOUT"
    ANALYSIS_UNSUPPORTED_SYNTAX = "ANALYSIS_UNSUPPORTED_SYNTAX"
    ANALYSIS_NO_ISSUES_FOUND    = "ANALYSIS_NO_ISSUES_FOUND"

    # ML layer
    ML_MODEL_NOT_LOADED         = "ML_MODEL_NOT_LOADED"
    ML_INFERENCE_FAILED         = "ML_INFERENCE_FAILED"
    ML_LOW_CONFIDENCE           = "ML_LOW_CONFIDENCE"
    ML_FEATURE_EXTRACTION_ERROR = "ML_FEATURE_EXTRACTION_ERROR"

    # System / infrastructure
    SYSTEM_DATABASE_ERROR       = "SYSTEM_DATABASE_ERROR"
    SYSTEM_CACHE_MISS           = "SYSTEM_CACHE_MISS"
    SYSTEM_RATE_LIMIT_EXCEEDED  = "SYSTEM_RATE_LIMIT_EXCEEDED"
    SYSTEM_DEPENDENCY_FAILURE   = "SYSTEM_DEPENDENCY_FAILURE"
    SYSTEM_UNKNOWN              = "SYSTEM_UNKNOWN"


# ---------------------------------------------------------------------------
# Score Thresholds
# ---------------------------------------------------------------------------

class ScoreThreshold:
    """
    Numeric thresholds used by the engine and ML layers to classify
    code quality, confidence, and severity.

    All values are in the range [0.0, 1.0] unless noted.
    """

    # Code quality bands
    QUALITY_EXCELLENT: Final[float] = 0.90
    QUALITY_GOOD:      Final[float] = 0.75
    QUALITY_FAIR:      Final[float] = 0.50
    QUALITY_POOR:      Final[float] = 0.25   # below this → critical

    # ML confidence gates
    ML_CONFIDENCE_HIGH:   Final[float] = 0.85
    ML_CONFIDENCE_MEDIUM: Final[float] = 0.60
    ML_CONFIDENCE_LOW:    Final[float] = 0.40  # below this → flag for review

    # Severity scores (engine issues, 0–10 scale)
    SEVERITY_CRITICAL: Final[int] = 9
    SEVERITY_HIGH:     Final[int] = 7
    SEVERITY_MEDIUM:   Final[int] = 4
    SEVERITY_LOW:      Final[int] = 1

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: Final[int] = 60
    RATE_LIMIT_BURST:               Final[int] = 10

    # File / payload limits
    MAX_FILE_SIZE_BYTES:  Final[int] = 1_048_576   # 1 MB
    MAX_FILES_PER_BATCH:  Final[int] = 50
    MAX_LINE_COUNT:       Final[int] = 10_000


# ---------------------------------------------------------------------------
# Supported Languages
# ---------------------------------------------------------------------------

@unique
class Language(str, Enum):
    """Programming languages supported by the analysis engine."""
    PYTHON     = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA       = "java"
    CPP        = "cpp"
    GO         = "go"
    RUST       = "rust"


# ---------------------------------------------------------------------------
# Config / Environment Variable Keys
# ---------------------------------------------------------------------------

class ConfigKey:
    """
    Names of environment variables consumed by the application.

    IMPORTANT: These are KEY NAMES only — never store actual secret values here.
    Load values at runtime via os.environ.get(ConfigKey.DATABASE_URL).
    """

    # Supabase
    SUPABASE_URL:              Final[str] = "SUPABASE_URL"
    SUPABASE_ANON_KEY:         Final[str] = "SUPABASE_ANON_KEY"
    SUPABASE_SERVICE_ROLE_KEY: Final[str] = "SUPABASE_SERVICE_ROLE_KEY"

    # Database (direct connection, if used alongside Supabase)
    DATABASE_URL:        Final[str] = "DATABASE_URL"
    DATABASE_POOL_SIZE:  Final[str] = "DATABASE_POOL_SIZE"

    # Cache
    REDIS_URL:           Final[str] = "REDIS_URL"
    CACHE_TTL_SECONDS:   Final[str] = "CACHE_TTL_SECONDS"

    # Auth / security
    JWT_SECRET_KEY:      Final[str] = "JWT_SECRET_KEY"
    JWT_ALGORITHM:       Final[str] = "JWT_ALGORITHM"
    JWT_EXPIRY_MINUTES:  Final[str] = "JWT_EXPIRY_MINUTES"
    ALLOWED_ORIGINS:     Final[str] = "ALLOWED_ORIGINS"

    # ML
    ML_MODEL_PATH:       Final[str] = "ML_MODEL_PATH"
    ML_DEVICE:           Final[str] = "ML_DEVICE"           # "cpu" | "cuda"
    ML_BATCH_SIZE:       Final[str] = "ML_BATCH_SIZE"

    # Engine
    ENGINE_TIMEOUT_SEC:  Final[str] = "ENGINE_TIMEOUT_SEC"
    ENGINE_WORKERS:      Final[str] = "ENGINE_WORKERS"

    # Observability
    LOG_LEVEL:           Final[str] = "LOG_LEVEL"
    SENTRY_DSN:          Final[str] = "SENTRY_DSN"
    OTEL_ENDPOINT:       Final[str] = "OTEL_ENDPOINT"

    # Feature flags
    FEATURE_ML_ENABLED:  Final[str] = "FEATURE_ML_ENABLED"
    FEATURE_BETA_UI:     Final[str] = "FEATURE_BETA_UI"


# ---------------------------------------------------------------------------
# Default Config Values  (safe, non-secret fallbacks)
# ---------------------------------------------------------------------------

class ConfigDefault:
    """Fallback values used when an env var is not set."""
    DATABASE_POOL_SIZE:  Final[int]   = 5
    CACHE_TTL_SECONDS:   Final[int]   = 300        # 5 minutes
    JWT_ALGORITHM:       Final[str]   = "HS256"
    JWT_EXPIRY_MINUTES:  Final[int]   = 60
    ENGINE_TIMEOUT_SEC:  Final[int]   = 30
    ENGINE_WORKERS:      Final[int]   = 4
    ML_BATCH_SIZE:       Final[int]   = 32
    ML_DEVICE:           Final[str]   = "cpu"
    LOG_LEVEL:           Final[str]   = "INFO"
    FEATURE_ML_ENABLED:  Final[bool]  = False
    FEATURE_BETA_UI:     Final[bool]  = False
