/**
 * Thin client for the /api/exam/* endpoints in routers/exam.py.
 * No answer-key data ever flows through here — that's enforced server-side,
 * this file just mirrors the schemas in schemas.py.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api/exam";

export interface Subject {
  id: string;
  code: string;
  name_ar: string;
  name_en: string;
  icon: string | null;
}

export interface Level {
  id: string;
  index: number;
  difficulty: "easy" | "medium" | "hard";
  questions_per_attempt: number;
  time_limit_seconds: number;
}

export interface Option {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  text: string;
  options: Option[];
}

export interface ExamSession {
  attempt_id: string;
  subject_code: string;
  level_index: number;
  expires_at: string;
  time_limit_seconds_per_question: number;
  questions: Question[];
}

export interface ExamResult {
  attempt_id: string;
  score: number;
  total_questions: number;
  pct: number;
  passed: boolean;
  rank_label: string;
  certificate_id: string | null;
  certificate_url: string | null;
}

export interface CertificateVerification {
  valid: boolean;
  trainee_name?: string;
  subject_name_en?: string;
  level_difficulty?: string;
  pct?: number;
  issued_at?: string;
  institute_name?: string;
  revoked: boolean;
}

async function apiFetch<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...opts.headers },
    credentials: "include", // send auth cookie/JWT
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export const examApi = {
  listSubjects: (instituteId: string) =>
    apiFetch<Subject[]>(`/subjects?institute_id=${instituteId}`),

  listLevels: (subjectId: string) =>
    apiFetch<Level[]>(`/subjects/${subjectId}/levels`),

  startExam: (payload: {
    trainee_name: string;
    trainee_email: string;
    trainee_id_number: string;
    level_id: string;
  }, lang: "ar" | "en" = "ar") =>
    apiFetch<ExamSession>(`/start?lang=${lang}`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  submitAnswer: (
    attemptId: string,
    payload: { question_id: string; selected_option_id: string | null; time_taken_seconds?: number }
  ) =>
    apiFetch<{ question_id: string; received: boolean }>(`/${attemptId}/answer`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  sendCheatSignal: (attemptId: string, event: "tab_hidden" | "fullscreen_exit") =>
    apiFetch<{ ok: boolean }>(`/${attemptId}/cheat-signal`, {
      method: "POST",
      body: JSON.stringify({ event }),
    }),

  submitExam: (attemptId: string, lang: "ar" | "en" = "ar") =>
    apiFetch<ExamResult>(`/${attemptId}/submit?lang=${lang}`, { method: "POST" }),

  verifyCertificate: (code: string) =>
    apiFetch<CertificateVerification>(`/verify/${code}`),
};
