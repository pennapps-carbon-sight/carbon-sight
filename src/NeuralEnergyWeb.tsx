import { useMemo, useState } from "react";
import { motion } from "framer-motion";

type Energy = "sustainable" | "balanced" | "intensive";
type Model = { id: string; label: string; energy: Energy };

type Props = {
  models: Model[];
  width?: number;   // viewBox width (SVG scales responsively)
  height?: number;  // viewBox height
  className?: string;
};

const ENERGY: Record<Energy, { color: string; label: string }> = {
  sustainable: { color: "#10B981", label: "Sustainable" },
  balanced: { color: "#F59E0B", label: "Balanced" },
  intensive: { color: "#F87171", label: "Intensive" },  
};

// tiny deterministic helpers
function hash(s: string) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function rand01(seed: number) {
  // Mulberry32
  seed = (seed + 0x6D2B79F5) >>> 0;
  let t = (seed += 0x6D2B79F5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

export default function NeuralEnergyWeb({
  models,
  width = 1000,
  height = 420,
  className,
}: Props) {
  const [hoverId, setHoverId] = useState<string | null>(null);

  const layout = useMemo(() => {
    const cx = width / 2;
    const cy = height / 2;
    const R = Math.min(width, height) * 0.46;

    // Spider-web: spokes + polygonal (slightly noisy) rings
    const SPOKES = 18;
    const RINGS = 6; // number of concentric webs
    const ringsR = Array.from({ length: RINGS }, (_, i) => R * ((i + 1) / (RINGS + 0.5)));

    // Base angles
    const angles = Array.from({ length: SPOKES }, (_, i) => (i / SPOKES) * Math.PI * 2 - Math.PI / 2);

    // “Web” polygons with slight noise to feel organic
    const ringPolys: { d: string }[] = [];
    for (let j = 0; j < RINGS; j++) {
      const pts: [number, number][] = [];
      for (let i = 0; i < SPOKES; i++) {
        const s = (j + 1) * 1000 + i * 7;
        const jitter = (rand01(s) - 0.5) * (R * 0.02);
        const rr = ringsR[j] + jitter;
        const x = cx + Math.cos(angles[i]) * rr;
        const y = cy + Math.sin(angles[i]) * rr;
        pts.push([x, y]);
      }
      const d = `M ${pts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(" L ")} Z`;
      ringPolys.push({ d });
    }

    // radial lines (spokes)
    const spokes: { x1: number; y1: number; x2: number; y2: number }[] = [];
    for (let i = 0; i < SPOKES; i++) {
      const x1 = cx + Math.cos(angles[i]) * ringsR[0] * 0.25; // small inner hub
      const y1 = cy + Math.sin(angles[i]) * ringsR[0] * 0.25;
      const x2 = cx + Math.cos(angles[i]) * ringsR[RINGS - 1];
      const y2 = cy + Math.sin(angles[i]) * ringsR[RINGS - 1];
      spokes.push({ x1, y1, x2, y2 });
    }

    // Node placement: choose a ring by energy, then a spoke (deterministic)
    type Node = Model & { x: number; y: number; r: number; ringIdx: number; spokeIdx: number };
    const nodes: Node[] = [];
    models.forEach((m) => {
      const h = hash(m.id);
      // energy -> ring band
      let ringIdx: number;
      if (m.energy === "intensive") ringIdx = 1;                // inner
      else if (m.energy === "balanced") ringIdx = 3 + (h % 2);  // mid
      else ringIdx = 5;                                         // outer
      ringIdx = Math.min(RINGS - 1, Math.max(1, ringIdx));

      const spokeIdx = h % SPOKES;
      const baseR = ringsR[ringIdx];
      const a = angles[spokeIdx] + (rand01(h) - 0.5) * (Math.PI / SPOKES) * 0.6; // slight angular jitter
      const rr = baseR + (rand01(h ^ 1337) - 0.5) * (R * 0.03);                    // radial jitter

      nodes.push({
        ...m,
        ringIdx,
        spokeIdx,
        x: cx + Math.cos(a) * rr,
        y: cy + Math.sin(a) * rr,
        r: 7.5,
      });
    });

    // Links: neighbor along ring + cross-ring along same spoke + one diagonal chord
    type Link = { a: Node; b: Node };
    const links: Link[] = [];

    // group nodes by ring
    const byRing: Node[][] = Array.from({ length: RINGS }, () => []);
    nodes.forEach((n) => byRing[n.ringIdx].push(n));
    byRing.forEach((ring) => ring.sort((a, b) => a.spokeIdx - b.spokeIdx));

    // ring neighbors
    byRing.forEach((ring) => {
      for (let i = 0; i < ring.length; i++) {
        const a = ring[i];
        const b = ring[(i + 1) % ring.length];
        if (a && b && a.id !== b.id) links.push({ a, b });
      }
    });

    // cross-ring (same spoke, closest ring)
    nodes.forEach((n) => {
      const target = nodes
        .filter((m) => m.spokeIdx === n.spokeIdx && m.ringIdx !== n.ringIdx)
        .sort((m1, m2) => Math.abs(m1.ringIdx - n.ringIdx) - Math.abs(m2.ringIdx - n.ringIdx))[0];
      if (target) links.push({ a: n, b: target });
    });

    // diagonal chords for extra webby feel
    nodes.forEach((n) => {
      const targetSpoke = (n.spokeIdx + 3) % SPOKES;
      const choice = nodes.find((m) => m.spokeIdx === targetSpoke && Math.abs(m.ringIdx - n.ringIdx) <= 2);
      if (choice) links.push({ a: n, b: choice });
    });

    return { cx, cy, R, ringPolys, spokes, nodes, links };
  }, [models, width, height]);

  return (
    <div className={`relative ${className || ""}`}>
      {/* Subtle immersive background (glow + scan) */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(1200px 320px at 50% 10%, rgba(16,185,129,0.15), transparent 60%)",
        }}
      />

      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Model energy network"
        className="w-full h-auto"
      >
        <defs>
          {/* web stroke gradient */}
          <linearGradient id="webStroke" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#94A3B8" stopOpacity="0.22" />
            <stop offset="1" stopColor="#FFFFFF" stopOpacity="0.16" />
          </linearGradient>
          {/* link shimmer */}
          <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#FFFFFF" stopOpacity="0.18" />
            <stop offset="1" stopColor="#FFFFFF" stopOpacity="0.36" />
          </linearGradient>
          {/* glow */}
          <filter id="g" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="b" />
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          {/* moving scan overlay */}
          <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#fff" stopOpacity="0" />
            <stop offset=".5" stopColor="#fff" stopOpacity=".08" />
            <stop offset="1" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
          <mask id="scanMask">
            <rect x="0" y="0" width={width} height={height} fill="url(#scan)" />
          </mask>
        </defs>

        {/* spider web: rings */}
        <g>
          {layout.ringPolys.map((p, i) => (
            <path
              key={i}
              d={p.d}
              fill="none"
              stroke="url(#webStroke)"
              strokeWidth={0.8}
              opacity={0.9}
            />
          ))}
        </g>

        {/* spider web: spokes */}
        <g>
          {layout.spokes.map((s, i) => (
            <line
              key={i}
              x1={s.x1}
              y1={s.y1}
              x2={s.x2}
              y2={s.y2}
              stroke="url(#webStroke)"
              strokeWidth={0.75}
              opacity={0.9}
            />
          ))}
        </g>

        {/* animated shimmer across the web */}
        <g mask="url(#scanMask)">
          <motion.rect
            x={-width}
            y={0}
            width={width * 0.8}
            height={height}
            fill="url(#scan)"
            initial={{ x: -width }}
            animate={{ x: width }}
            transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
          />
        </g>

        {/* links */}
        <g style={{ mixBlendMode: "screen" }}>
          {layout.links.map((ln, i) => {
            const active =
              hoverId && (ln.a.id === hoverId || ln.b.id === hoverId);
            return (
              <motion.line
                key={i}
                x1={ln.a.x}
                y1={ln.a.y}
                x2={ln.b.x}
                y2={ln.b.y}
                stroke="url(#edge)"
                strokeWidth={active ? 2 : 1.1}
                strokeLinecap="round"
                initial={{ opacity: 0.22 }}
                animate={{ opacity: [0.22, 0.45, 0.22] }}
                transition={{
                  duration: 2 + ((i * 97) % 50) / 25,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            );
          })}
        </g>

        {/* nodes */}
        <g>
          {layout.nodes.map((n) => {
            const c = ENERGY[n.energy].color;
            const isHover = hoverId === n.id;
            const label = `${n.label}  •  ${ENERGY[n.energy].label}`;
            // simple tooltip positioning (shift left if near right edge)
            const shiftLeft = n.x > width * 0.7 ? -1 : 1;

            return (
              <g
                key={n.id}
                transform={`translate(${n.x}, ${n.y})`}
                onMouseEnter={() => setHoverId(n.id)}
                onMouseLeave={() => setHoverId(null)}
                onFocus={() => setHoverId(n.id)}
                onBlur={() => setHoverId(null)}
                tabIndex={0}
                role="button"
                aria-label={label}
                className="cursor-pointer"
              >
                {/* halo */}
                <motion.circle
                  r={isHover ? n.r + 10 : n.r + 7}
                  fill={c}
                  opacity={0.18}
                  filter="url(#g)"
                  animate={isHover ? { opacity: [0.2, 0.35, 0.2] } : { opacity: 0.18 }}
                  transition={{ duration: 1.6, repeat: Infinity }}
                />
                {/* core */}
                <circle r={n.r} fill={c} />
                {/* inner seed */}
                <circle r={2.3} fill="black" opacity={0.6} />

                {/* tooltip */}
                {isHover && (
                  <g transform={`translate(${12 * shiftLeft}, -14)`}>
                    <rect
                      x={shiftLeft < 0 ? -Math.max(86, label.length * 6.7) : 0}
                      y={-18}
                      rx={6}
                      ry={6}
                      width={Math.max(86, label.length * 6.7)}
                      height={24}
                      fill="rgba(2,6,23,0.95)"
                      stroke="rgba(255,255,255,0.14)"
                    />
                    <text
                      x={(shiftLeft < 0 ? -Math.max(86, label.length * 6.7) : 0) + 8}
                      y={0}
                      fontSize={11}
                      fill="#E5E7EB"
                      style={{ fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, Arial" }}
                    >
                      {n.label}
                      <tspan fill="#94A3B8">{`  •  ${ENERGY[n.energy].label}`}</tspan>
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </g>

        {[...Array(10)].map((_, i) => {
          const startX = (i * 83) % width;
          return (
            <motion.circle
              key={i}
              r={1.4}
              cx={startX}
              cy={(i * 53) % height}
              fill="#A7F3D0"
              initial={{ opacity: 0.0, cy: (i * 53) % height }}
              animate={{ opacity: [0.0, 0.5, 0.0], cy: [(i * 53) % height, ((i * 53) % height) - 30, (i * 53) % height] }}
              transition={{ duration: 3 + (i % 5), repeat: Infinity, delay: i * 0.2 }}
              style={{ mixBlendMode: "screen" }}
            />
          );
        })}
      </svg>
    </div>
  );
}