/**
 * extension/src/lib/supabaseClient.ts
 * =====================================
 * Supabase client wrapper for the VS Code extension layer.
 *
 * - Credentials are loaded from VS Code extension settings / environment only.
 * - Exposes a single anon client — the extension NEVER holds the service-role key.
 * - The admin/service-role client lives exclusively in the Python backend.
 *
 * Dependencies:
 *   npm install @supabase/supabase-js
 *
 * Usage:
 *   import { getSupabaseClient } from './lib/supabaseClient';
 *   const client = getSupabaseClient();
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import * as vscode from 'vscode';
import { ConfigKey, ConfigDefault } from '../constants';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Shape of the Supabase config resolved at runtime. */
interface SupabaseConfig {
  url: string;
  anonKey: string;
}

// ---------------------------------------------------------------------------
// Config resolution
// ---------------------------------------------------------------------------

/**
 * Resolves Supabase credentials in priority order:
 *   1. VS Code workspace/user settings  (kaizencode.supabaseUrl / kaizencode.supabaseAnonKey)
 *   2. Process environment variables     (SUPABASE_URL / SUPABASE_ANON_KEY)
 *
 * Throws if either value is missing so failures are loud and early.
 */
function resolveConfig(): SupabaseConfig {
  const settings = vscode.workspace.getConfiguration('kaizencode');

  const url =
    settings.get<string>(ConfigKey.SUPABASE_URL) ||
    process.env['SUPABASE_URL'] ||
    '';

  const anonKey =
    settings.get<string>(ConfigKey.SUPABASE_ANON_KEY) ||
    process.env['SUPABASE_ANON_KEY'] ||
    '';

  if (!url) {
    throw new Error(
      `Supabase URL is not configured. ` +
      `Set '${ConfigKey.SUPABASE_URL}' in VS Code settings or the SUPABASE_URL env var.`
    );
  }

  if (!anonKey) {
    throw new Error(
      `Supabase anon key is not configured. ` +
      `Set '${ConfigKey.SUPABASE_ANON_KEY}' in VS Code settings or the SUPABASE_ANON_KEY env var.`
    );
  }

  return { url, anonKey };
}

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

let _client: SupabaseClient | null = null;

/**
 * Returns the shared Supabase anon client.
 * Initialised once on first call; subsequent calls return the cached instance.
 *
 * The client respects Row Level Security (RLS) — it operates as the
 * authenticated user or the anon role.
 */
export function getSupabaseClient(): SupabaseClient {
  if (!_client) {
    const { url, anonKey } = resolveConfig();
    _client = createClient(url, anonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: false, // not a browser — extension context
      },
    });
  }
  return _client;
}

/**
 * Resets the cached client (useful when credentials change at runtime,
 * e.g. user updates settings).
 */
export function resetSupabaseClient(): void {
  _client = null;
}
