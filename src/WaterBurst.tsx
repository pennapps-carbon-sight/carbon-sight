import React, { useMemo } from "react";

type Props = { show: boolean; color: "green" | "red" };

export default function WaterBurst({ show, color }: Props) {
  const burstKey = useMemo(() => (show ? Date.now() : 0), [show]);
  if (!show) return null;

  return (
    <div
      key={burstKey}
      data-color={color}
      className="wb-allow-motion pointer-events-none absolute inset-0 z-0" /* behind z-20 content */
      aria-hidden
    >
      <svg
        className="h-full w-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        shapeRendering="geometricPrecision"
      >
        {/* Vertical: smooth rise → hold → fall */}
        <g className="wb-rise">
          {/* Horizontal: seamless rightward scroll using two tiles */}
          <g>
            <g>
              {/* tile A at x=0 */}
              <path
                className="wb-surface"
                d="
                  M 0 22
                  C 16 16, 34 28, 50 22
                  S 84 16, 100 22
                  L 100 100
                  L 0 100
                  Z
                "
              />
              {/* tile B at x=-100 (covers the left when we slide right) */}
              <path
                className="wb-surface"
                transform="translate(-100 0)"
                d="
                  M 0 22
                  C 16 16, 34 28, 50 22
                  S 84 16, 100 22
                  L 100 100
                  L 0 100
                  Z
                "
              />
              {/* Smooth rightward scroll: shift group +100 user units */}
              <animateTransform
                attributeName="transform"
                type="translate"
                from="0 0"
                to="100 0"
                dur="4s"
                repeatCount="indefinite"
                calcMode="linear"
              />
            </g>
          </g>
        </g>
      </svg>
    </div>
  );
}