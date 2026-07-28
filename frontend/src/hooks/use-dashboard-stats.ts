"use client";
import { useQuery } from "@tanstack/react-query";
import { candidatesApi } from "@/lib/api/candidates";
import { mciApi } from "@/lib/api/mci";
import type { Candidate, MciResult } from "@/types/mci";

export interface DashboardStats {
  candidates: Candidate[];
  mciByUser: Record<number, MciResult | null>;
  totalCandidates: number;
  scoredCandidates: number;
  averageMci: number;
  levelCounts: Record<string, number>;
  categoryAverages: { key: string; label: string; value: number }[];
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: async (): Promise<DashboardStats> => {
      const candidates = await candidatesApi.list();
      const mciResults = await Promise.all(
        candidates.map((c) => mciApi.getSavedMci(c.id).catch(() => null))
      );

      const mciByUser: Record<number, MciResult | null> = {};
      candidates.forEach((c, i) => {
        mciByUser[c.id] = mciResults[i];
      });

      const scored = mciResults.filter((r): r is MciResult => r !== null);
      const averageMci = scored.length
        ? Math.round((scored.reduce((sum, r) => sum + r.mci_score, 0) / scored.length) * 10) / 10
        : 0;

      const levelCounts: Record<string, number> = {};
      scored.forEach((r) => {
        levelCounts[r.level] = (levelCounts[r.level] || 0) + 1;
      });

      const categoryTotals: Record<string, { label: string; sum: number; count: number }> = {};
      scored.forEach((r) => {
        r.categories.forEach((c) => {
          if (!categoryTotals[c.key]) categoryTotals[c.key] = { label: c.label, sum: 0, count: 0 };
          categoryTotals[c.key].sum += c.sub_score_0_100;
          categoryTotals[c.key].count += 1;
        });
      });
      const categoryAverages = Object.entries(categoryTotals).map(([key, v]) => ({
        key,
        label: v.label,
        value: Math.round((v.sum / v.count) * 10) / 10,
      }));

      return {
        candidates,
        mciByUser,
        totalCandidates: candidates.length,
        scoredCandidates: scored.length,
        averageMci,
        levelCounts,
        categoryAverages,
      };
    },
  });
}
