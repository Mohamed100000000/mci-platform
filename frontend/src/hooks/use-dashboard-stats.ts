"use client";
import { useQuery } from "@tanstack/react-query";
import { traineesApi } from "@/lib/api/trainees";
import { mciApi } from "@/lib/api/mci";
import type { Trainee, MciScore } from "@/types/mci";

export interface DashboardStats {
  candidates: Trainee[];
  mciByTrainee: Record<string, MciScore | null>;
  totalCandidates: number;
  scoredCandidates: number;
  averageMci: number;
  // نطاقات درجة MCI (0-1000) بدلاً من "مستويات" وهمية غير موجودة في
  // الـbackend الحقيقي — نفس بنية الرسم البياني القديمة، مصدر بيانات حقيقي.
  scoreRangeCounts: Record<string, number>;
  categoryAverages: { key: string; label: string; value: number }[];
}

const SCORE_RANGES: [string, number, number][] = [
  ["0–249", 0, 249],
  ["250–499", 250, 499],
  ["500–749", 500, 749],
  ["750–1000", 750, 1000],
];

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: async (): Promise<DashboardStats> => {
      const candidates = await traineesApi.list();
      const mciResults = await Promise.all(
        candidates.map((c) => mciApi.getLatest(c.id).catch(() => null))
      );

      const mciByTrainee: Record<string, MciScore | null> = {};
      candidates.forEach((c, i) => {
        mciByTrainee[c.id] = mciResults[i];
      });

      const scored = mciResults.filter((r): r is MciScore => r !== null);
      const averageMci = scored.length
        ? Math.round((scored.reduce((sum, r) => sum + r.total_score, 0) / scored.length) * 10) / 10
        : 0;

      const scoreRangeCounts: Record<string, number> = {};
      scored.forEach((r) => {
        const range = SCORE_RANGES.find(([, min, max]) => r.total_score >= min && r.total_score <= max);
        const label = range ? range[0] : "Other";
        scoreRangeCounts[label] = (scoreRangeCounts[label] || 0) + 1;
      });

      const componentLabels: { key: keyof MciScore; label: string }[] = [
        { key: "attendance_component", label: "Attendance" },
        { key: "competency_component", label: "Competency" },
        { key: "certification_component", label: "Certification" },
        { key: "recency_component", label: "Recency" },
      ];
      const categoryAverages = componentLabels.map(({ key, label }) => {
        const values = scored.map((r) => r[key] as number);
        const value = values.length
          ? Math.round((values.reduce((sum, v) => sum + v, 0) / values.length) * 10) / 10
          : 0;
        return { key: key as string, label, value };
      });

      return {
        candidates,
        mciByTrainee,
        totalCandidates: candidates.length,
        scoredCandidates: scored.length,
        averageMci,
        scoreRangeCounts,
        categoryAverages,
      };
    },
  });
}
