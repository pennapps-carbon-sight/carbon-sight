import { useEffect, useState, useCallback } from "react";
import { fetchTeamAverages } from "../api/metrics";
import type { TeamAverages } from "../models/metrics";

export function useTeamAverages() {
  const [data, setData] = useState<TeamAverages[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const rows = await fetchTeamAverages();
      setData(rows);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return { data, error, loading, reload: load };
}