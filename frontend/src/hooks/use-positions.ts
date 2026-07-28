"use client";
import { useQuery } from "@tanstack/react-query";
import { positionsApi } from "@/lib/api/positions";

export function usePositions() {
  return useQuery({ queryKey: ["positions"], queryFn: positionsApi.list });
}

export function useReadiness(userId: number | null, positionId: number | null) {
  return useQuery({
    queryKey: ["readiness", userId, positionId],
    queryFn: () => positionsApi.getReadiness(userId as number, positionId as number),
    enabled: userId !== null && positionId !== null,
  });
}

export function useSkillGap(userId: number | null, positionId: number | null) {
  return useQuery({
    queryKey: ["skill-gap", userId, positionId],
    queryFn: () => positionsApi.getSkillGap(userId as number, positionId as number),
    enabled: userId !== null && positionId !== null,
  });
}
