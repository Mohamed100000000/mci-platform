"use client";

import { useEffect, useRef, useState } from "react";
import { examApi, type ExamSession, type Question } from "../lib/examApi";
import { ShipWheelProgress } from "./ShipWheelProgress";

interface ExamRunnerProps {
  session: ExamSession;
  lang: "ar" | "en";
  onFinished: () => void;
}

const STRINGS = {
  ar: { scoreLbl: "نقطة", qOf: (a: number, b: number) => `السؤال ${a} / ${b}` },
  en: { scoreLbl: "points", qOf: (a: number, b: number) => `Question ${a} / ${b}` },
};

export function ExamRunner({ session, lang, onFinished }: ExamRunnerProps) {
  const s = STRINGS[lang];
  const [current, setCurrent] = useState(0);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [locked, setLocked] = useState(false);
  const [timeLeft, setTimeLeft] = useState(session.time_limit_seconds_per_question);
  const questionStartRef = useRef<number>(Date.now());

  const question: Question = session.questions[current];
  const total = session.questions.length;

  useEffect(() => {
    if (new Date() > new Date(session.expires_at)) {
      void finish();
    }
  }, []);

  useEffect(() => {
    setTimeLeft(session.time_limit_seconds_per_question);
    questionStartRef.current = Date.now();
    setSelected(null);
    setLocked(false);
    const interval = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(interval);
          handleAnswer(null);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [current]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden) void examApi.sendCheatSignal(session.attempt_id, "tab_hidden");
    };
    const onFullscreenChange = () => {
      if (!document.fullscreenElement) void examApi.sendCheatSignal(session.attempt_id, "fullscreen_exit");
    };
    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("fullscreenchange", onFullscreenChange);
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("fullscreenchange", onFullscreenChange);
    };
  }, [session.attempt_id]);

  async function handleAnswer(optionId: string | null) {
    if (locked) return;
    setLocked(true);
    setSelected(optionId);
    const timeTaken = Math.round((Date.now() - questionStartRef.current) / 1000);
    try {
      await examApi.submitAnswer(session.attempt_id, {
        question_id: question.id,
        selected_option_id: optionId,
        time_taken_seconds: timeTaken,
      });
    } catch {
    }
    setAnsweredCount((c) => c + 1);

    setTimeout(() => {
      if (current + 1 >= total) {
        void finish();
      } else {
        setCurrent((c) => c + 1);
      }
    }, 500);
  }

  async function finish() {
    await examApi.submitExam(session.attempt_id, lang);
    onFinished();
  }

  return (
    <div>
      <div className="mb-4">
        <ShipWheelProgress progress={answeredCount / total} score={answeredCount} scoreLabel={s.scoreLbl} />
      </div>

      <div className="flex items-center justify-between text-xs text-mci-off-white/60 mb-3 px-1">
        <span className="rounded-full border border-mci-sky-blue/40 bg-mci-sky-blue/15 px-2.5 py-1 font-bold text-mci-sky-blue-light">
          {session.subject_code} · L{session.level_index + 1}
        </span>
        <span className={`tabular-nums ${timeLeft <= 5 ? "text-mci-coral font-bold" : ""}`}>
          ⏱ {timeLeft}
        </span>
      </div>

      <div className="rounded-xl bg-mci-parchment text-mci-ink p-5 shadow-lg">
        <div className="text-[11px] font-bold uppercase tracking-wide text-mci-steel mb-2">
          {s.qOf(current + 1, total)}
        </div>
        <div className="text-[17.5px] font-bold leading-relaxed mb-4">{question.text}</div>

        <div className="flex flex-col gap-2.5">
          {question.options.map((opt) => (
            <button
              key={opt.id}
              disabled={locked}
              onClick={() => handleAnswer(opt.id)}
              className={`flex items-center justify-between rounded-[10px] border px-4 py-3 text-start text-[14.5px] transition-colors ${
                selected === opt.id
                  ? "border-mci-sky-blue bg-white"
                  : "border-mci-parchment-dim bg-mci-off-white hover:border-mci-sky-blue hover:bg-white"
              } ${locked ? "opacity-85 pointer-events-none" : ""}`}
            >
              <span>{opt.text}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
