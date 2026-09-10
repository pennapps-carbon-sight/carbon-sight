import { createClient, type SupabaseClient } from "@supabase/supabase-js";

declare global {
  // Prevent multiple clients during Vite HMR
  var __CS_SUPABASE__: SupabaseClient | undefined;
}

const url = import.meta.env.VITE_SUPABASE_URL;
const anon = import.meta.env.VITE_SUPABASE_ANON_KEY;

/** False when the Supabase env vars are missing — App renders <MissingEnv /> instead. */
export const supabaseConfigured = Boolean(url && anon);

/**
 * createClient() throws when the URL is absent, and this module is imported at
 * startup — so without a guard a missing .env takes the whole app down before
 * App.tsx can show its configuration screen. When unconfigured we hand back a
 * proxy that stays quiet on import and explains itself if anything calls it.
 */
function unconfigured(): SupabaseClient {
  const fail = () => {
    throw new Error(
      "Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY (see .env.example)."
    );
  };
  return new Proxy({} as SupabaseClient, { get: fail, apply: fail });
}

export const supabase: SupabaseClient = supabaseConfigured
  ? (globalThis.__CS_SUPABASE__ ??= createClient(url as string, anon as string, {
      auth: { persistSession: true, autoRefreshToken: true, storageKey: "cs-auth" },
    }))
  : unconfigured();
