"""
api/db/supabase_client.py
=========================
Supabase client wrapper for the Python backend (api, engine, ml layers).

- All credentials are loaded exclusively from environment variables.
- Exposes two singletons:
    supabase        → anon/public client  (safe for user-scoped operations)
    supabase_admin  → service-role client (server-side only, never expose to client)
- Import either singleton directly:
    from api.db.supabase_client import supabase, supabase_admin

Dependencies:
    pip install supabase python-dotenv
"""

import os
import logging
from functools import lru_cache

from dotenv import load_dotenv
from supabase import create_client, Client

from shared.constants import ConfigKey

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()  # loads .env into os.environ (no-op in production where vars are injected)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _require_env(key: str) -> str:
    """Fetch a required env var; raise clearly if missing."""
    value = os.environ.get(key, "").strip()
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: '{key}'. "
            "Ensure it is set in your .env file or deployment environment."
        )
    return value


# ---------------------------------------------------------------------------
# Client factories (cached — one instance per process)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Returns the anon/public Supabase client.
    Safe for operations that respect Row Level Security (RLS).
    """
    url  = _require_env(ConfigKey.SUPABASE_URL)
    key  = _require_env(ConfigKey.SUPABASE_ANON_KEY)
    client = create_client(url, key)
    logger.info("Supabase anon client initialised (url=%s)", url)
    return client


@lru_cache(maxsize=1)
def get_supabase_admin_client() -> Client:
    """
    Returns the service-role Supabase client.
    Bypasses RLS — use ONLY for trusted server-side operations.
    Never expose this client or its key to the frontend.
    """
    url  = _require_env(ConfigKey.SUPABASE_URL)
    key  = _require_env(ConfigKey.SUPABASE_SERVICE_ROLE_KEY)
    client = create_client(url, key)
    logger.info("Supabase admin client initialised (url=%s)", url)
    return client


# ---------------------------------------------------------------------------
# Module-level singletons (convenience imports)
# ---------------------------------------------------------------------------

supabase: Client       = get_supabase_client()
supabase_admin: Client = get_supabase_admin_client()
