import { supabase } from "../lib/supabaseClient";
import type { TeamAverages, TeamName, UserMetrics, Profile } from "../models/metrics";

/* ------------ Reads (Dashboard) ------------ */
export async function fetchTeamAverages(): Promise<TeamAverages[]> {
  // Preferred path: your SECURITY DEFINER RPC
  const { data, error } = await supabase.rpc("get_team_averages");
  if (error) throw new Error(error.message);

  // Normalize + order for consistent UI
  const order: TeamName[] = ["ML", "Engineering", "Finance", "Research", "HR"];
  const rows = (data ?? []).map((r: any) => ({
    team: String(r.team) as TeamName,
    user_count: Number(r.user_count ?? 0),
    avg_co2_kg: Number(r.avg_co2_kg ?? 0),
    avg_cost_usd: Number(r.avg_cost_usd ?? 0),
    avg_latency_ms: Number(r.avg_latency_ms ?? 0),
  }));

  const byTeam = new Map(rows.map(r => [r.team, r]));
  return order.map(t => byTeam.get(t)).filter(Boolean) as TeamAverages[];
}

/* ------------ Profile helpers (per-user) ------------ */
export async function getMyProfile(): Promise<Profile | null> {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  const { data, error } = await supabase
    .from("profiles")
    .select("id, team, created_at")
    .eq("id", user.id)
    .maybeSingle();

  if (error) throw new Error(error.message);
  return data as Profile | null;
}

export async function setMyTeam(team: TeamName): Promise<void> {
  // Uses your RPC set_my_team(team_t)
  const { error } = await supabase.rpc("set_my_team", { p_team: team });
  if (error) throw new Error(error.message);
}

/* ------------ Per-user totals (write from Chat, etc.) ------------ */
export async function upsertMyTotals(totals: {
  total_co2_kg: number;
  total_cost_usd: number;
  total_latency_ms: number;
}) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Not signed in");

  const payload = { user_id: user.id, ...totals };
  const { error } = await supabase.from("user_metrics").upsert([payload], { onConflict: "user_id" });
  if (error) throw new Error(error.message);
}

/** Convenience: add deltas to my existing totals (read → add → upsert). */
export async function bumpMyTotals(delta: {
  co2_kg?: number;
  cost_usd?: number;
  latency_ms?: number;
}) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Not signed in");

  const { data, error } = await supabase
    .from("user_metrics")
    .select("*")
    .eq("user_id", user.id)
    .maybeSingle();
  if (error) throw new Error(error.message);

  const current: UserMetrics | null = (data as any) ?? null;

  const next = {
    total_co2_kg: round((current?.total_co2_kg ?? 0) + (delta.co2_kg ?? 0)),
    total_cost_usd: round((current?.total_cost_usd ?? 0) + (delta.cost_usd ?? 0)),
    total_latency_ms: Math.round((current?.total_latency_ms ?? 0) + (delta.latency_ms ?? 0)),
  };

  await upsertMyTotals(next);
}

/* ------------ utils ------------ */
function round(n: number, dp = 4) {
  const p = Math.pow(10, dp);
  return Math.round(n * p) / p;
}