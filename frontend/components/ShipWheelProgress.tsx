"use client";

import { motion } from "framer-motion";

interface ShipWheelProgressProps {
  /** 0 to 1 */
  progress: number;
  score: number;
  scoreLabel: string;
}

const CIRC = 346; // matches the r=55 circle circumference used in the original game

export function ShipWheelProgress({ progress, score, scoreLabel }: ShipWheelProgressProps) {
  const offset = CIRC - CIRC * progress;
  const rotation = progress * 360;

  return (
    <div className="relative w-[132px] h-[132px] mx-auto">
      <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
        <circle cx="60" cy="60" r="55" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
        <motion.circle
          cx="60"
          cy="60"
          r="55"
          fill="none"
          stroke="#c8952f"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={CIRC}
          initial={false}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
          style={{ filter: "drop-shadow(0 0 6px rgba(200,149,47,0.6))" }}
        />
      </svg>

      <motion.div
        className="absolute top-1/2 left-1/2 w-[78px] h-[78px] -translate-x-1/2 -translate-y-1/2"
        initial={false}
        animate={{ rotate: rotation }}
        transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
      >
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="10" fill="#c8952f" />
          <circle cx="50" cy="50" r="38" fill="none" stroke="#e6c374" strokeWidth="5" />
          <g stroke="#e6c374" strokeWidth="5" strokeLinecap="round">
            <line x1="50" y1="12" x2="50" y2="30" />
            <line x1="50" y1="70" x2="50" y2="88" />
            <line x1="12" y1="50" x2="30" y2="50" />
            <line x1="70" y1="50" x2="88" y2="50" />
            <line x1="22" y1="22" x2="34" y2="34" />
            <line x1="66" y1="66" x2="78" y2="78" />
            <line x1="78" y1="22" x2="66" y2="34" />
            <line x1="34" y1="66" x2="22" y2="78" />
          </g>
        </svg>
      </motion.div>

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
        <div className="font-azda-display text-[22px] font-bold text-azda-brass-light leading-none">
          {score}
        </div>
        <div className="text-[9px] text-azda-off-white/50 tracking-wide">{scoreLabel}</div>
      </div>
    </div>
  );
}
