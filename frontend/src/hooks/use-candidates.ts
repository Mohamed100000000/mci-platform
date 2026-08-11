"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { traineesApi } from "@/lib/api/trainees";
import type { TraineeCreateInput } from "@/types/mci";

// Function names kept as "candidate" for UI continuity — the data is real
// Trainee data from /api/v1/trainees (id is a uuid string, not a number).
export function useCandidates() {
  return useQuery({ queryKey: ["trainees"], queryFn: traineesApi.list });
}

export function useCandidate(id: string | null) {
  return useQuery({
    queryKey: ["trainees", id],
    queryFn: () => traineesApi.get(id as string),
    enabled: id !== null,
  });
}

export function useCreateCandidate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: TraineeCreateInput) => traineesApi.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainees"] });
    },
  });
}
