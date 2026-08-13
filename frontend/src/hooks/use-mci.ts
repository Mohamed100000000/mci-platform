"use client";
import { useQuery } from "@tanstack/react-query";
import { mciApi } from "@/lib/api/mci";

export function useLatestMci(traineeId: string | null) {
  return useQuery({
    queryKey: ["mci-latest", traineeId],
    queryFn: () => mciApi.getLatest(traineeId as string),
    enabled: traineeId !== null,
  });
}
