"use client";

import { useMemo, useState } from "react";
import type { Subject } from "../lib/examApi";

interface SubjectGridProps {
  subjects: Subject[];
  lang: "ar" | "en";
  onSelect: (subject: Subject) => void;
}

const STRINGS = {
  ar: { prompt: "اختر المادة التي تريد اختبار نفسك فيها:", search: "ابحث عن اسم الدورة...", noResults: "لا توجد نتائج مطابقة" },
  en: { prompt: "Choose the subject you want to be tested on:", search: "Search for a course...", noResults: "No matching results" },
};

export function SubjectGrid({ subjects, lang, onSelect }: SubjectGridProps) {
  const s = STRINGS[lang];
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return subjects;
    return subjects.filter((sub) =>
      `${sub.code} ${sub.name_ar} ${sub.name_en}`.toLowerCase().includes(q)
    );
  }, [subjects, query]);

  return (
    <div className="rounded-xl bg-azda-parchment text-azda-ink p-6 shadow-lg">
      <p className="text-sm mb-3">{s.prompt}</p>

      <div className="flex items-center gap-2 rounded-full border border-azda-parchment-dim bg-azda-off-white px-3.5 py-2 mb-3 focus-within:border-azda-brass">
        <span className="text-xs opacity-60">🔍</span>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={s.search}
          className="flex-1 bg-transparent text-[13.5px] outline-none"
        />
      </div>

      <div className="grid gap-1.5" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(78px, 1fr))" }}>
        {filtered.map((sub) => (
          <button
            key={sub.id}
            onClick={() => onSelect(sub)}
            className="rounded-[10px] border border-azda-parchment-dim bg-azda-off-white px-1 py-2 text-center hover:border-azda-brass hover:-translate-y-0.5 hover:shadow-md transition-all"
          >
            <div className="text-[15px] leading-none mb-0.5">{sub.icon}</div>
            <div className="font-azda-display text-[10.5px] font-bold text-azda-navy-deep leading-tight">
              {sub.code}
            </div>
            <div className="text-[8px] text-[#7a7260] mt-0.5 leading-tight line-clamp-2">
              {lang === "ar" ? sub.name_ar : sub.name_en}
            </div>
          </button>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center text-[12.5px] text-[#8a8070] py-3.5">{s.noResults}</div>
      )}
    </div>
  );
}
