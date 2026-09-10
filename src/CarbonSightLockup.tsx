// CarbonSightLockup.tsx
import React, { useId } from "react";

type Energy = "sustainable" | "balanced" | "intensive";
type Side = "left" | "right";

export default function CarbonSightLockup({
  energy = "sustainable",
  side = "left",
  width = 220,
  height = 36,
  className = "",
}: {
  energy?: Energy;
  side?: Side;
  width?: number;
  height?: number;
  className?: string;
}) {
  const uid = useId();
  const accent = energy === "intensive" ? "#F87171" : "#10B981";
  const text = "#E5E7EB";

  // layout
  const iconW = 140;
  const gap = 20;
  const totalW = 700; // roomy viewBox; scales down via width/height props

  const textX = side === "left" ? iconW + gap : 0;
  const iconX = side === "left" ? 0 : 520; // place icon after text on the right
  const baselineY = 92;

  return (
    <svg
      viewBox={`0 0 ${totalW} 140`}
      width={width}
      height={height}
      className={className}
      role="img"
      aria-label="CarbonSight"
    >
      <defs>
        <linearGradient id={`cs-grad-${uid}`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0.7" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <clipPath id={`cs-eye-${uid}`}>
          <path d="M0,52 C30,0 110,0 140,52 C110,104 30,104 0,52Z" />
        </clipPath>
      </defs>

      <style>{`
        .cs-text {
          font: 700 64px/1.1 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Inter,Arial;
          fill: ${text};
          letter-spacing: .5px;
        }
        .cs-accent { fill: ${accent}; }
        .cs-scan { fill: url(#cs-grad-${uid}); mix-blend-mode: screen; opacity: .75; }
        @media (prefers-reduced-motion: no-preference){
          .cs-sweep { animation: cs-sweep 3.6s linear infinite; }
          @keyframes cs-sweep { from { transform: translateX(-220px) } to { transform: translateX(220px) } }
        }
      `}</style>

      {/* word */}
      <text className="cs-text" x={textX} y={baselineY} textAnchor="start">
        CarbonSight
      </text>

      {/* icon */}
      <g transform={`translate(${iconX},18)`} aria-hidden="true">
        <path
          d="M0,52 C30,0 110,0 140,52 C110,104 30,104 0,52Z"
          fill="none" stroke={accent} strokeWidth={5} opacity=".9"
        />
        <circle cx="70" cy="52" r="26" fill="none" stroke={accent} strokeWidth={5} opacity=".55" />
        <path className="cs-accent" d="M70 36c10 8 14 17 14 26 0 9-4 18-14 26-10-8-14-17-14-26 0-9 4-18 14-26Z" />
        <g clipPath={`url(#cs-eye-${uid})`} className="cs-sweep">
          <rect className="cs-scan" x={-220} y={0} width={220} height={104} />
        </g>
      </g>
    </svg>
  );
}