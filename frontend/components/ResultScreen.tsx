"use client";

import { motion } from "framer-motion";
import type { ExamResult } from "../lib/examApi";

interface ResultScreenProps {
  result: ExamResult;
  traineeName: string;
  traineeId: string;
  subjectLabel: string;
  lang: "ar" | "en";
  logoSrc: string;
  onRetry: () => void;
  onOtherSubject: () => void;
}

const STRINGS = {
  ar: {
    scoreLbl: "إجابات صحيحâ",
    pctLbl: "نسبة النجاح",
    passed: "شهادة اجتياز",
    attempt: "محاولة - لم يتم الاجتياز بعد",
    retry: "أعد المحاولة 🔁",
    other: "مادة أخرى",
    print: "🖨 طباعة / حفظ الشهادة PDF",
    idLbl: "رقم الهوية/الجواز:",
    dateLbl: "تاريخ الاختبار:",
  },
  en: {
    scoreLbl: "Correct answers",
    pctLbl: "Success rate",
    passed: "Certificate of Achievement",
    attempt: "Attempt — Not yet passed",
    retry: "Retry 🔁",
    other: "Other subject",
    print: "🖨 Print / Save Certificate PDF",
    idLbl: "ID/Passport No.:",
    dateLbl: "Test Date:",
  },
};

export function ResultScreen({
  result,
  traineeName,
  traineeId,
  subjectLabel,
  lang,
  logoSrc,
  onRetry,
  onOtherSubject,
}: ResultScreenProps) {
  const s = STRINGS[lang];
  const dateStr = new Date().toLocaleDateString(lang === "ar" ? "ar-EG" : "en-US", { year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="rounded-xl bg-mci-parchment text-mci-ink p-6 text-center shadow-lg">
      <div className="mb-5 rounded-lg border-2 border-mci-sky-blue p-5" style={{ background: "#f4f7fb" }}>
        <img src={logoSrc} alt="MCI Platform" className="h-8 mx-auto mb-2.5 opacity-90" />

        <motion.div
          initial={{ scale: 2.2, rotate: -15, opacity: 0 }}
          animate={{ scale: 1, rotate: 0, opacity: 1 }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          className="mx-auto mb-2.5 flex h-[58px] w-[58px] items-center justify-center rounded-full text-2xl shadow-md"
          style={{ background: "linear-gradient(180deg,#a9cdf0,#4a90d9)" }}
        >
          👋
        </motion.div>

        <div className="text-[10.5px] font-bold uppercase tracking-widest text-mci-steel">
          {subjectLabel}
        </div>
        <div className="font-mci-display text-[22px] font-bold text-mci-navy-deep mb-1">
          {result.rank_label}
        </div>
        <div className="mb-2.5 text-[10px] font-bold uppercase tracking-wide text-mci-sky-blue">
          {result.passed ? s.passed : s.attempt}
        </div>

        <div className="my-2.5 border-y border-dashed border-mci-sky-blue/40 py-2">
          <div className="text-sm font-bold text-mci-navy-deep">{traineeName}</div>
          <div className="text-[11px] text-[#5a5140] mt-0.5">
            {s.idLbl} {traineeId}
          </div>
          <div className="text-[10.5px] text-[#7a7260] mt-0.5">
            {s.dateLbl} {dateStr}
          </div>
        </div>

        <div className="mt-2 flex justify-center gap-5">
          <Stat value={`${result.score} / ${result.total_questions}`} label={s.scoreLbl} />
          <Stat value={`${result.pct}%`} label={s.pctLbl} />
        </div>
      </div>

      {result.passed && result.certificate_url && (
        <div className="mb-2">
          <a
            href={result.certificate_url}
            target="_blank"
            rel="noreferrer"
            className="inline-block rounded-full bg-gradient-to-b from-mci-sky-blue-light to-mci-sky-blue px-7 py-2.5 text-[13.5px] font-bold text-mci-navy-deep shadow-md"
          >
            {s.print}
          </a>
        </div>
      )}

      <div className="mt-3 flex flex-wrap justify-center gap-2.5">
        <button
          onClick={onRetry}
          className="rounded-full bg-gradient-to-b from-mci-sky-blue-light to-mci-sky-blue px-6 py-2.5 text-[13.5px] font-bold text-mci-navy-deep shadow-md"
        >
          {s.retry}
        </button>
        <button
          onClick={onOtherSubject}
          className="rounded-full border-[1.5px] border-mci-sky-blue px-6 py-2.5 text-[13.5px] font-bold text-mci-sky-blue-light"
        >
          {s.other}
        </button>
      </div>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="font-mci-display text-[19px] font-bold text-mci-steel">{value}</div>
      <div className="text-[10px] text-[#7a7260]">{label}</div>
    </div>
  );
}
