export type TeamName = "ML" | "Engineering" | "Finance" | "Research" | "HR";

export interface Profile {
  id: string;              // auth.users.id
  team: TeamName;
  created_at: string;
}

export interface UserMetrics {
  user_id: string;         // auth.users.id
  total_co2_kg: number;
  total_cost_usd: number;
  total_latency_ms: number;
  updated_at: string;
}

export interface TeamAverages {
  team: TeamName;
  num_entries: number;
  avg_co2_kg: number;
  avg_cost_usd: number;
  avg_latency_ms: number;
}