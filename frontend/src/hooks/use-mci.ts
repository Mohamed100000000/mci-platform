"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { mciApi, type FactorScoreInput } from "@/lib/api/mci";

export function useFactorGroups() {
  return useQuery({ queryKey: ["factors"], queryFn: mciApi.listFactors, staleTime: Infinity });
}

export function useLatestFactorScores(userId: number | null) {
  return useQuery({
    queryKey: ["factor-scores", userId],
    queryFn: () => mciApi.getLatestFactorScores(userId as number),
    enabled: userId !== null,
  });
}

export function useSubmitFactorScores(userId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (scores: FactorScoreInput[]) => mciApi.submitFactorScores(userId as number, scores),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["factor-scores", userId] });
    },
  });
}

export function useSavedMci(userId: number | null) {
  return useQuery({
    queryKey: ["mci", userId],
    queryFn: () => mciApi.getSavedMci(userId as number),
    enabled: userId !== null,
  });
}

export function useComputeMci(userId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => mciApi.computeMci(userId as number),
    onSuccess: (data) => {
      queryClient.setQueryData(["mci", userId], data);
    },
  });
}
