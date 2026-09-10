import { useEffect, useState } from "react";
import { setMyTeam, getMyProfile } from "../api/metrics";
import type { TeamName } from "../models/metrics";

const TEAMS: TeamName[] = ["ML", "Engineering", "Finance", "Research", "HR"];

export default function TeamPicker() {
  const [team, setTeam] = useState<TeamName | "">("");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const p = await getMyProfile();
      if (p?.team) setTeam(p.team);
    })();
  }, []);

  async function save() {
    if (!team) return;
    setSaving(true);
    setMsg(null);
    try {
      await setMyTeam(team);
      setMsg("Saved!");
    } catch (e: any) {
      setMsg(e?.message ?? String(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <label className="text-xs text-slate-400">Team</label>
      <select
        className="rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-xs outline-none"
        value={team}
        onChange={(e) => setTeam(e.target.value as TeamName)}
      >
        <option value="" disabled>Select team…</option>
        {TEAMS.map(t => <option key={t} value={t}>{t}</option>)}
      </select>
      <button
        onClick={save}
        disabled={!team || saving}
        className="rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-black hover:bg-emerald-400 disabled:opacity-60"
      >
        {saving ? "Saving…" : "Save"}
      </button>
      {msg && <span className="text-xs text-slate-400 ml-2">{msg}</span>}
    </div>
  );
}