"use client";

import { useEffect, useState } from "react";
import { AzdaFrame } from "@/components/exam/AzdaFrame";
import { LoginPanel } from "@/components/exam/LoginPanel";
import { SubjectGrid } from "@/components/exam/SubjectGrid";
import { LevelSelect } from "@/components/exam/LevelSelect";
import { ExamRunner } from "@/components/exam/ExamRunner";
import { ResultScreen } from "@/components/exam/ResultScreen";
import { examApi, type Subject, type Level, type ExamSession, type ExamResult } from "@/lib/exam/examApi";

// TODO: replace with your real institute UUID / a value pulled from route params
const INSTITUTE_ID = process.env.NEXT_PUBLIC_AZDA_INSTITUTE_ID ?? "";
const LOGO_SRC = "/azda-logo.png"; // TODO: point at your actual asset

type Screen = "login" | "subjects" | "levels" | "exam" | "results";

const STRINGS = {
  ar: { title: "تحدي القبطان", subtitle: "اختبر معلوماتك في مواد التدريب البحري STCW" },
  en: { title: "Captain's Challenge", subtitle: "Test your knowledge of STCW maritime training subjects" },
};

export default function ExamPage() {
  const [lang, setLang] = useState<"ar" | "en">("ar");
  const [screen, setScreen] = useState<Screen>("login");

  const [trainee, setTrainee] = useState<{ name: string; email: string; idNumber: string } | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [levels, setLevels] = useState<Level[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<Level | null>(null);
  const [session, setSession] = useState<ExamSession | null>(null);
  const [result, setResult] = useState<ExamResult | null>(null);

  useEffect(() => {
    if (screen === "subjects" && subjects.length === 0) {
      examApi.listSubjects(INSTITUTE_ID).then(setSubjects).catch(console.error);
    }
  }, [screen]);

  async function handleLogin(data: { name: string; email: string; idNumber: string }) {
    setTrainee(data);
    setScreen("subjects");
  }

  async function handleSelectSubject(subject: Subject) {
    setSelectedSubject(subject);
    const lvls = await examApi.listLevels(subject.id);
    setLevels(lvls);
    setScreen("levels");
  }

  async function handleSelectLevel(level: Level) {
    if (!trainee) return;
    setSelectedLevel(level);
    const newSession = await examApi.startExam(
      {
        trainee_name: trainee.name,
        trainee_email: trainee.email,
        trainee_id_number: trainee.idNumber,
        level_id: level.id,
      },
      lang
    );
    setSession(newSession);
    setScreen("exam");
  }

  async function handleFinished() {
    if (!session) return;
    const res = await examApi.submitExam(session.attempt_id, lang);
    setResult(res);
    setScreen("results");
  }

  function goHome() {
    setScreen("subjects");
    setSelectedSubject(null);
    setSelectedLevel(null);
    setSession(null);
    setResult(null);
  }

  function retrySameLevel() {
    if (selectedLevel) void handleSelectLevel(selectedLevel);
  }

  return (
    <AzdaFrame
      logoSrc={LOGO_SRC}
      title={STRINGS[lang].title}
      subtitle={STRINGS[lang].subtitle}
      lang={lang}
      onToggleLang={() => setLang((l) => (l === "ar" ? "en" : "ar"))}
      onHome={goHome}
    >
      {screen === "login" && <LoginPanel lang={lang} onSubmit={handleLogin} />}

      {screen === "subjects" && (
        <SubjectGrid subjects={subjects} lang={lang} onSelect={handleSelectSubject} />
      )}

      {screen === "levels" && selectedSubject && (
        <LevelSelect
          levels={levels}
          subjectCode={selectedSubject.code}
          lang={lang}
          onSelect={handleSelectLevel}
          onBack={() => setScreen("subjects")}
        />
      )}

      {screen === "exam" && session && (
        <ExamRunner session={session} lang={lang} onFinished={handleFinished} />
      )}

      {screen === "results" && result && trainee && selectedSubject && selectedLevel && (
        <ResultScreen
          result={result}
          traineeName={trainee.name}
          traineeId={trainee.idNumber}
          subjectLabel={`${selectedSubject.code} — L${selectedLevel.index + 1}`}
          lang={lang}
          logoSrc={LOGO_SRC}
          onRetry={retrySameLevel}
          onOtherSubject={goHome}
        />
      )}
    </AzdaFrame>
  );
}
