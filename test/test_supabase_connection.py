"""
test/test_supabase_connection.py
=================================
Tests the Supabase connection by verifying:
  1. Required environment variables are present and correctly formatted.
  2. The Supabase client can be instantiated.
  3. A live network request reaches the Supabase project (queries a known table).

Run:
    pip install supabase python-dotenv
    python -m pytest test/test_supabase_connection.py -v
"""

import os
import re
import pytest
from dotenv import load_dotenv

# Load .env from repo root (one level up from KaizenCode/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().strip('"')
# Use service role key for tests — bypasses RLS so we can verify schema/connectivity
# without needing policies in place yet. Never expose this key client-side.
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip().strip('"')
    or os.getenv("SUPABASE_ANON_KEY", "").strip().strip('"')
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _url_is_valid(url: str) -> bool:
    """Returns True only if the URL has no angle brackets and looks like a real Supabase URL."""
    return bool(
        url
        and "<" not in url
        and ">" not in url
        and re.match(r"https://[a-z]{20}\.supabase\.co$", url)
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSupabaseEnvVars:
    """Validate environment variable presence and format before attempting connection."""

    def test_url_is_set(self):
        assert SUPABASE_URL, "SUPABASE_URL is missing from .env"

    def test_url_has_no_angle_brackets(self):
        assert "<" not in SUPABASE_URL and ">" not in SUPABASE_URL, (
            f"SUPABASE_URL contains angle brackets — fix it in .env.\n"
            f"  Current value : {SUPABASE_URL}\n"
            f"  Expected format: https://<your-project-id>.supabase.co"
        )

    def test_url_format(self):
        assert _url_is_valid(SUPABASE_URL), (
            f"SUPABASE_URL does not match expected Supabase format.\n"
            f"  Current value : {SUPABASE_URL}\n"
            f"  Expected      : https://xxxxxxxxxxxxxxxxxxxx.supabase.co"
        )

    def test_anon_key_is_set(self):
        assert SUPABASE_KEY, "SUPABASE_ANON_KEY is missing from .env"

    def test_anon_key_is_jwt(self):
        parts = SUPABASE_KEY.split(".")
        assert len(parts) == 3, (
            "SUPABASE_ANON_KEY does not look like a valid JWT (expected 3 dot-separated parts)."
        )


class TestSupabaseClient:
    """Instantiate the Supabase client."""

    @pytest.fixture(autouse=True)
    def skip_if_bad_url(self):
        if not _url_is_valid(SUPABASE_URL):
            pytest.skip("Skipping client tests — SUPABASE_URL is invalid (fix angle brackets first).")

    def test_client_instantiation(self):
        from supabase import create_client, Client
        client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        assert client is not None, "Supabase client failed to instantiate."


class TestSupabaseLiveConnection:
    """
    Live network tests — query real tables defined in sqlschema.sql.
    These tests require the schema to be applied to the Supabase project.
    """

    @pytest.fixture(autouse=True)
    def skip_if_bad_url(self):
        if not _url_is_valid(SUPABASE_URL):
            pytest.skip("Skipping live tests — SUPABASE_URL is invalid (fix angle brackets first).")

    @pytest.fixture
    def client(self):
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)

    def test_can_reach_users_table(self, client):
        """SELECT from users table — confirms DB is reachable and schema exists."""
        response = client.table("users").select("id").limit(1).execute()
        # A successful response has a .data attribute (list, even if empty)
        assert hasattr(response, "data"), "Response missing .data — unexpected response shape."
        assert isinstance(response.data, list), "Expected response.data to be a list."

    def test_can_reach_user_balances_table(self, client):
        response = client.table("user_balances").select("user_id").limit(1).execute()
        assert isinstance(response.data, list)

    def test_can_reach_repositories_table(self, client):
        response = client.table("repositories").select("id").limit(1).execute()
        assert isinstance(response.data, list)

    def test_can_reach_analysis_runs_table(self, client):
        response = client.table("analysis_runs").select("id").limit(1).execute()
        assert isinstance(response.data, list)

    def test_can_reach_marketplace_items_table(self, client):
        response = client.table("marketplace_items").select("id").limit(1).execute()
        assert isinstance(response.data, list)
