/**
 * Design tokens for the MCI Platform (Maritime Competency Index).
 * Palette derived from the lighthouse logo: deep navy background,
 * sky-blue accents, white/parchment text surfaces.
 */

export const mciTheme = {
  colors: {
    navyDeep: "#0b1f3a",
    navyMid: "#12315a",
    steel: "#1c4a78",
    skyBlue: "#4a90d9",
    skyBlueLight: "#a9cdf0",
    parchment: "#f4f7fb",
    parchmentDim: "#dce6f2",
    ink: "#0f1f30",
    coral: "#c1462f",
    sea: "#2f8f7c",
    offWhite: "#f6f9fc",
  },
  fonts: {
    display: "Georgia, 'Times New Roman', serif",
    body: "Tahoma, 'Segoe UI', Arial, sans-serif",
  },
} as const;

/**
 * Rank thresholds - shared with the backend's rank_label() in
 * services/exam_engine.py. Keep these two in sync.
 */
export const RANKS = {
  captain: { min: 85, ar: "القبطان (Captain)", en: "The Captain" },
  officer: { min: 60, ar: "ضابط بحري (Officer)", en: "Marine Officer" },
  trainee: { min: 0, ar: "بحار متدرب (Trainee)", en: "Trainee Seafarer" },
} as const;

export function rankFor(pct: number, lang: "ar" | "en" = "ar") {
  if (pct >= RANKS.captain.min) return RANKS.captain[lang];
  if (pct >= RANKS.officer.min) return RANKS.officer[lang];
  return RANKS.trainee[lang];
}
