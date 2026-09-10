# CarbonSight

**Cut AI emissions, not quality.**

Every LLM call costs money, time, and carbon. Most teams only ever see the first one. CarbonSight
puts all three next to each other — cost, latency, and CO₂ — and makes the trade-off visible at the
moment you choose a model, not in a quarterly report nobody reads.

Built at **PennApps 2025**.

## The idea

Not every prompt needs the biggest model. Summarising a paragraph on a 70B model burns energy that
a 7B model would have spent a fraction of, for an answer nobody could tell apart.

So the chat exposes three tiers and labels them by what they actually cost the planet:

| Model | Tier | |
|---|---|---|
| `eco-7b` — Eco (GreenAI-7B) | **sustainable** | Cheap, fast, low emissions |
| `mix-13b` — Balanced (Mix-13B) | **balanced** | The middle |
| `xl-70b` — Performance (XL-70B) | **intensive** | When the answer genuinely needs it |

Every call is recorded. The dashboard then shows the consequences per team, so a leader can see
that Research spends 4× what Finance does on comparable work — and decide whether that is a
justified trade or a defaulting habit.

## What's in it

**Chat** (`/chat`) — Pick a tier per conversation. Collapsible sidebar,
<kbd>⌘/Ctrl</kbd>+<kbd>B</kbd> to collapse, <kbd>⌘/Ctrl</kbd>+<kbd>N</kbd> for a new chat.

**Dashboard** (`/dashboard`) — Average cost (USD), latency (ms), and CO₂ (kg) by team, read from the
`user_metrics` view. Five teams: ML, Engineering, Finance, Research, HR.

**Landing** (`/`) — With `NeuralEnergyWeb`, an animated visualisation of the model network.

Both `/chat` and `/dashboard` require a session and redirect to the landing page without one.

## Stack

React 19 · TypeScript · Vite · Supabase (auth + Postgres) · Recharts · Framer Motion ·
Tailwind · lucide-react

## Run it

```bash
npm install
cp .env.example .env    # then fill in your Supabase project
npm run dev
```

| Variable | |
|---|---|
| `VITE_SUPABASE_URL` | Supabase → Project Settings → API |
| `VITE_SUPABASE_ANON_KEY` | The **anon** key. It ships to the browser by design — protect data with row-level security, not by hiding it. |

Without both, the app boots into a "missing configuration" state instead of crashing, so you can
still see the landing page.

### Supabase

Needs a `user_metrics` view exposing `team`, `avg_cost_usd`, `avg_latency_ms`, `avg_co2_kg`, and
`num_entries`, over a per-user metrics table. Enable row-level security on the underlying tables
and scope policies to `auth.uid()` — the anon key is public, so RLS is the only thing standing
between a visitor and everyone's usage data.

```bash
npm run typecheck   # tsc -b
npm run lint        # eslint
npm run build       # tsc -p tsconfig.build.json && vite build
```

## Team

Built at PennApps 2025 by [@devank-yadav](https://github.com/devank-yadav),
[@Irapathak](https://github.com/Irapathak), [@Advita9](https://github.com/Advita9), and Aarav Raina.

## Status

Hackathon project, and it reads like one in places — the model tiers are a fixed list rather than a
live registry, and emissions come from per-model constants rather than measurement. The idea it is
testing is whether showing carbon next to cost changes which model people pick.
