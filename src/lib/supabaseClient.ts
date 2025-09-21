import { createClient, type SupabaseClient } from "@supabase/supabase-js";

declare global {
  // Prevent multiple clients during Vite HMR
  var __CS_SUPABASE__: SupabaseClient | undefined;
}

const url = import.meta.env.VITE_SUPABASE_URL!;
const anon = import.meta.env.VITE_SUPABASE_ANON_KEY!;

export const supabase: SupabaseClient =
  globalThis.__CS_SUPABASE__ ??
  (globalThis.__CS_SUPABASE__ = createClient(url, anon, {
    auth: { persistSession: true, autoRefreshToken: true, storageKey: "cs-auth" },
  }));