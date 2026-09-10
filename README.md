<h1 align="center">CarbonSight</h1>
<p align="center"><strong>Make every token greener.</strong><br>
Pick lower-carbon models without sacrificing quality — and see what it saved.</p>
<p align="center"><em>Built at PennApps 2025.</em></p>

![CarbonSight landing page](docs/landing.png)

## The problem

Every LLM call costs three things: money, time, and carbon. Teams see the first one on an invoice,
feel the second in latency graphs, and never see the third at all.

So the default is to reach for the biggest model available. Summarising a paragraph on a 70B model
burns energy a 7B model would have spent a fraction of, for an answer nobody could tell apart —
and nothing in the tooling ever surfaces that trade.

CarbonSight puts all three side by side at the moment you pick a model, and shows the consequences
per team afterwards.

## The concept

| | |
|---|---|
| **Greener by default** | Carbon-aware routing picks cleaner regions and efficient models automatically — live grid carbon signal, auto model/region selection, per-request opt-out |
| **Real-time signals** | Balance quality, latency, and energy at runtime, not at deploy time — smart fallbacks and retries, burst-aware throttling |
| **Impact you can see** | Energy (Wh), CO₂e, and CSI — a Carbon Sensitivity Index — trended across teams and models, with exportable reports |
| **Rewards that pay back** | Earn credits for choosing greener lanes without losing quality — auto accrual, payout history, per-model incentives |
| **Drop-in API & SDKs** | Keep your stack; plug into existing calls via HTTP proxy or SDK, with policy and quota controls and audit-ready logs |
| **Guardrails & policies** | Org-level carbon budgets, allow/deny model lists, region pinning |

## What's built

This is a hackathon prototype, and it is honest about which half is real.

**Working end to end**

- **Supabase auth** — email sessions, with `/chat` and `/dashboard` gated behind them
- **Team dashboard** — average cost (USD), latency (ms), and CO₂ (kg) per team, read live from a
  `user_metrics` Postgres view across ML, Engineering, Finance, Research, and HR
- **Tiered model picker** — three lanes, labelled by what they cost the planet rather than by
  parameter count
- **Landing page** — with `NeuralEnergyWeb`, an animated model-network visualisation

| Model | Tier |
|---|---|
| `eco-7b` — Eco (GreenAI-7B) | **sustainable** |
| `mix-13b` — Balanced (Mix-13B) | **balanced** |
| `xl-70b` — Performance (XL-70B) | **intensive** |

**Simulated** — the chat itself. It is a demo shell, labelled as such in the UI: it returns a
canned reply rather than calling a model, and emissions come from per-model constants rather than
measurement. The routing, the SDK, and the rewards ledger are concept, not code.

![Chat with the tier picker and energy burst](docs/chat.png)

Picking a lane plays a colour burst — green for sustainable and balanced, red for intensive. It is
a small thing, but it is the whole thesis in one interaction: make the carbon cost of a choice
something you *feel* at the moment you make it.

## Stack

React 19 · TypeScript · Vite · Supabase (auth + Postgres) · Recharts · Framer Motion · Tailwind ·
lucide-react

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

Without both, the app boots into a "missing configuration" state rather than crashing, so the
landing page still renders.

**Supabase** — needs a `user_metrics` view exposing `team`, `avg_cost_usd`, `avg_latency_ms`,
`avg_co2_kg`, and `num_entries` over a per-user metrics table. Enable row-level security on the
underlying tables and scope policies to `auth.uid()`: the anon key is public, so RLS is the only
thing between a visitor and everyone's usage data.

```bash
npm run typecheck   # tsc -b
npm run lint
npm run build
```

## Team

Built over 36 hours at **PennApps 2025** by
[@devank-yadav](https://github.com/devank-yadav) ·
[@Irapathak](https://github.com/Irapathak) ·
[@Advita9](https://github.com/Advita9) ·
Aarav Raina

[Devpost](https://devpost.com/software/carbonsight)
