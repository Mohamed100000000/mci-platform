import { apiClient } from "./client";
import type { Position, ReadinessResult, SkillGapResult } from "@/types/mci";

export const positionsApi = {
  list: async (): Promise<Position[]> => {
    const { data } = await apiClient.get<Position[]>("/api/positions");
    return data;
  },
  getReadiness: async (userId: number, positionId: number): Promise<ReadinessResult> => {
    const { data } = await apiClient.get<ReadinessResult>(`/api/users/${userId}/readiness/${positionId}`);
    return data;
  },
  getSkillGap: async (userId: number, positionId: number): Promise<SkillGapResult> => {
    const { data } = await apiClient.get<SkillGapResult>(`/api/users/${userId}/skill-gap/${positionId}`);
    return data;
  },
};
