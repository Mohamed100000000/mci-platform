import { apiClient } from "./client";
import type { FactorGroup, MciResult } from "@/types/mci";

export interface FactorScoreInput {
  factor_key: string;
  raw_score: number;
  evidence_type?: string;
  source?: string;
}

export const mciApi = {
  listFactors: async (): Promise<FactorGroup[]> => {
    const { data } = await apiClient.get<FactorGroup[]>("/api/factors");
    return data;
  },
  getLatestFactorScores: async (userId: number): Promise<Record<string, number>> => {
    const { data } = await apiClient.get<Record<string, number>>(`/api/users/${userId}/factors`);
    return data;
  },
  submitFactorScores: async (userId: number, scores: FactorScoreInput[]) => {
    const { data } = await apiClient.post(`/api/users/${userId}/factors`, { scores });
    return data;
  },
  computeMci: async (userId: number): Promise<MciResult> => {
    const { data } = await apiClient.post<MciResult>(`/api/users/${userId}/mci`);
    return data;
  },
  getSavedMci: async (userId: number): Promise<MciResult | null> => {
    try {
      const { data } = await apiClient.get<MciResult>(`/api/users/${userId}/mci`);
      return data;
    } catch {
      return null;
    }
  },
};
