/**
 * extension/src/constants.ts
 * ===========================
 * TypeScript mirror of shared/constants.py for the VS Code extension layer.
 *
 * Rules:
 *  - Keep in sync with shared/constants.py — any change there must be reflected here.
 *  - Never store secrets or tokens here; use VS Code SecretStorage for those.
 *  - All objects are frozen (Object.freeze) to prevent accidental mutation.
 */

// ---------------------------------------------------------------------------
// HTTP Status Codes
// ---------------------------------------------------------------------------

export const HttpStatus = Object.freeze({
  OK:                  200,
  CREATED:             201,
  NO_CONTENT:          204,
  BAD_REQUEST:         400,
  UNAUTHORIZED:        401,
  FORBIDDEN:           403,
  NOT_FOUND:           404,
  CONFLICT:            409,
  UNPROCESSABLE:       422,
  TOO_MANY_REQUESTS:   429,
  INTERNAL_ERROR:      500,
  SERVICE_UNAVAILABLE: 503,
} as const);

export type HttpStatusValue = typeof HttpStatus[keyof typeof HttpStatus];


// ---------------------------------------------------------------------------
// Application Error Codes
// ---------------------------------------------------------------------------

export const ErrorCode = Object.freeze({
  // Auth
  AUTH_INVALID_TOKEN:          "AUTH_INVALID_TOKEN",
  AUTH_TOKEN_EXPIRED:          "AUTH_TOKEN_EXPIRED",
  AUTH_INSUFFICIENT_SCOPE:     "AUTH_INSUFFICIENT_SCOPE",
  AUTH_USER_NOT_FOUND:         "AUTH_USER_NOT_FOUND",

  // Input validation
  INPUT_MISSING_FIELD:         "INPUT_MISSING_FIELD",
  INPUT_INVALID_TYPE:          "INPUT_INVALID_TYPE",
  INPUT_OUT_OF_RANGE:          "INPUT_OUT_OF_RANGE",
  INPUT_UNSUPPORTED_LANGUAGE:  "INPUT_UNSUPPORTED_LANGUAGE",
  INPUT_FILE_TOO_LARGE:        "INPUT_FILE_TOO_LARGE",
  INPUT_EMPTY_PAYLOAD:         "INPUT_EMPTY_PAYLOAD",

  // Code analysis (engine)
  ANALYSIS_PARSE_FAILED:       "ANALYSIS_PARSE_FAILED",
  ANALYSIS_TIMEOUT:            "ANALYSIS_TIMEOUT",
  ANALYSIS_UNSUPPORTED_SYNTAX: "ANALYSIS_UNSUPPORTED_SYNTAX",
  ANALYSIS_NO_ISSUES_FOUND:    "ANALYSIS_NO_ISSUES_FOUND",

  // ML layer
  ML_MODEL_NOT_LOADED:         "ML_MODEL_NOT_LOADED",
  ML_INFERENCE_FAILED:         "ML_INFERENCE_FAILED",
  ML_LOW_CONFIDENCE:           "ML_LOW_CONFIDENCE",
  ML_FEATURE_EXTRACTION_ERROR: "ML_FEATURE_EXTRACTION_ERROR",

  // System / infrastructure
  SYSTEM_DATABASE_ERROR:       "SYSTEM_DATABASE_ERROR",
  SYSTEM_CACHE_MISS:           "SYSTEM_CACHE_MISS",
  SYSTEM_RATE_LIMIT_EXCEEDED:  "SYSTEM_RATE_LIMIT_EXCEEDED",
  SYSTEM_DEPENDENCY_FAILURE:   "SYSTEM_DEPENDENCY_FAILURE",
  SYSTEM_UNKNOWN:              "SYSTEM_UNKNOWN",
} as const);

export type ErrorCodeValue = typeof ErrorCode[keyof typeof ErrorCode];


// ---------------------------------------------------------------------------
// Score Thresholds
// ---------------------------------------------------------------------------

export const ScoreThreshold = Object.freeze({
  // Code quality bands [0.0 – 1.0]
  QUALITY_EXCELLENT: 0.90,
  QUALITY_GOOD:      0.75,
  QUALITY_FAIR:      0.50,
  QUALITY_POOR:      0.25,

  // ML confidence gates [0.0 – 1.0]
  ML_CONFIDENCE_HIGH:   0.85,
  ML_CONFIDENCE_MEDIUM: 0.60,
  ML_CONFIDENCE_LOW:    0.40,

  // Severity scores [0 – 10]
  SEVERITY_CRITICAL: 9,
  SEVERITY_HIGH:     7,
  SEVERITY_MEDIUM:   4,
  SEVERITY_LOW:      1,

  // Rate limiting
  RATE_LIMIT_REQUESTS_PER_MINUTE: 60,
  RATE_LIMIT_BURST:               10,

  // File / payload limits
  MAX_FILE_SIZE_BYTES:  1_048_576,  // 1 MB
  MAX_FILES_PER_BATCH:  50,
  MAX_LINE_COUNT:       10_000,
} as const);


// ---------------------------------------------------------------------------
// Supported Languages
// ---------------------------------------------------------------------------

export const Language = Object.freeze({
  PYTHON:     "python",
  JAVASCRIPT: "javascript",
  TYPESCRIPT: "typescript",
  JAVA:       "java",
  CPP:        "cpp",
  GO:         "go",
  RUST:       "rust",
} as const);

export type LanguageValue = typeof Language[keyof typeof Language];


// ---------------------------------------------------------------------------
// Config / Environment / Extension Setting Keys
// ---------------------------------------------------------------------------

/**
 * Keys for VS Code workspace/user settings (contributes.configuration in package.json).
 * Reference these instead of raw strings to avoid typos.
 */
export const ConfigKey = Object.freeze({
  // Supabase
  SUPABASE_URL:        "kaizencode.supabaseUrl",
  SUPABASE_ANON_KEY:   "kaizencode.supabaseAnonKey",  // anon key only — service-role stays in backend

  // API
  API_BASE_URL:        "kaizencode.apiBaseUrl",
  API_TIMEOUT_MS:      "kaizencode.apiTimeoutMs",
  AUTH_TOKEN:          "kaizencode.authToken",         // stored in SecretStorage, not settings

  // Features
  ML_ENABLED:          "kaizencode.mlEnabled",
  BETA_UI_ENABLED:     "kaizencode.betaUiEnabled",

  // Misc
  LOG_LEVEL:           "kaizencode.logLevel",
  MAX_FILE_SIZE_BYTES: "kaizencode.maxFileSizeBytes",
  SUPPORTED_LANGUAGES: "kaizencode.supportedLanguages",
} as const);

export type ConfigKeyValue = typeof ConfigKey[keyof typeof ConfigKey];


// ---------------------------------------------------------------------------
// Default Config Values
// ---------------------------------------------------------------------------

export const ConfigDefault = Object.freeze({
  API_BASE_URL:        "http://localhost:8000",
  API_TIMEOUT_MS:      10_000,
  ML_ENABLED:          false,
  BETA_UI_ENABLED:     false,
  LOG_LEVEL:           "info",
  MAX_FILE_SIZE_BYTES: ScoreThreshold.MAX_FILE_SIZE_BYTES,
} as const);
