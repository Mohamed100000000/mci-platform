"use client";

import type { Level } from "../lib/examApi";

interface LevelSelectProps {
  levels: Level[];
  subjectCode: string;
  lang: "ar" | "en";
  onSelect: (level: Level) => void;
  onBack: () => void;
}

const STRINGS = {
  ar: {
    prompt: "اختر المستوى:",
    back: "↩ رجوع للمواد",
    levelName: (i: number) => `المستوى ${i + 1}`,
    difficulty: { easy: "سهل", medium: "متوسط", hard: "صعب" },
  },
  en: {
    prompt: "Choose a level:",
    back: "↩ Back to subjects",
    levelName: (i: number) => `Level ${i + 1}`,
    difficulty: { easy: "Easy", medium: "Medium", hard: "Hard" },
  },
};

const DOT_COLOR = { easy: "#2f8f7c", medium: "#4a90d9", hard: "#c1462f" };

export function LevelSelect({ levels, subjectCode, lang, onSelect, onBack }: LevelSelectProps) {
  const s = STRINGS[lang];

  return (
    <div className="rounded-xl bg-mci-parchment text-mci-ink p-6 shadow-lg">
      <p className="text-sm mb-3">{s.prompt}</p>

      <div className="flex flex-col gap-2">
        {levels.map((lvl) => (
          <button
            key={lvl.id}
            onClick={() => onSelect(lvl)}
            className="flex items-center justify-between rounded-lg border border-mci-parchment-dim bg-mci-off-white px-4 py-3 hover:border-mci-sky-blue hover:bg-white transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <span
                className="flex h-6.5 w-6.5 shrink-0 items-center justify-center rounded-full text-xs font-bold text-mci-off-white"
                style={{ backgroundColor: DOT_COLOR[lvl.difficulty], width: 26, height: 26 }}
              >
                {lvl.index + 1}
              </span>
              <div className="text-start">
                <div className="text-[13.5px] font-bold">
                  {s.levelName(lvl.index)} — {subjectCode}
                </div>
                <div className="text-[10.5px] text-[#7a7260]">{s.difficulty[lvl.difficulty]}</div>
              </div>
            </div>
            <span>▶</span>
          </button>
        ))}
      </div>

      <div
        onClick={onBack}
        className="mt-3.5 text-center text-xs text-mci-off-white/50 underline cursor-pointer"
      >
        {s.back}
      </div>
    </div>
  );
}
