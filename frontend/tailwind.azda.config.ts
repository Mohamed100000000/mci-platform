/**
 * Merge this into your existing tailwind.config.ts under theme.extend.
 * Do not replace your whole config - just add the colors and fontFamily
 * keys shown here to what you already have.
 */
import type { Config } from "tailwindcss";

const azdaExtend: Partial<Config["theme"]> = {
  extend: {
    colors: {
      "azda-navy-deep": "#0a1c30",
      "azda-navy-mid": "#123252",
      "azda-steel": "#1c4364",
      "azda-brass": "#c8952f",
      "azda-brass-light": "#e6c374",
      "azda-parchment": "#f3ecdb",
      "azda-parchment-dim": "#e3d9bd",
      "azda-ink": "#12212f",
      "azda-coral": "#c1462f",
      "azda-sea": "#2f8f7c",
      "azda-off-white": "#f6f1e4",
    },
    fontFamily: {
      "azda-display": ["Georgia", "Times New Roman", "serif"],
      "azda-body": ["Tahoma", "Segoe UI", "Arial", "sans-serif"],
    },
  },
};

export default azdaExtend;
