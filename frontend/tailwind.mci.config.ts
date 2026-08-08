/**
 * Merge this into your existing tailwind.config.ts under theme.extend.
 * Replaces the old tailwind.azda.config.ts - delete that file once this
 * is merged. Colors match lib/theme.ts (mciTheme).
 */
import type { Config } from "tailwindcss";

const mciExtend: Partial<Config["theme"]> = {
  extend: {
    colors: {
      "mci-navy-deep": "#0b1f3a",
      "mci-navy-mid": "#12315a",
      "mci-steel": "#1c4a78",
      "mci-sky-blue": "#4a90d9",
      "mci-sky-blue-light": "#a9cdf0",
      "mci-parchment": "#f4f7fb",
      "mci-parchment-dim": "#dce6f2",
      "mci-ink": "#0f1f30",
      "mci-coral": "#c1462f",
      "mci-sea": "#2f8f7c",
      "mci-off-white": "#f6f9fc",
    },
    fontFamily: {
      "mci-display": ["Georgia", "Times New Roman", "serif"],
      "mci-body": ["Tahoma", "Segoe UI", "Arial", "sans-serif"],
    },
  },
};

export default mciExtend;
