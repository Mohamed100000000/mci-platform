"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { candidatesApi } from "@/lib/api/candidates";
import type { CandidateCreateInput } from "@/types/mci";

export function useCandidates() {
  return useQuery({ queryKey: ["candidates"], queryFn: candidatesApi.list });
}

export function useCandidate(id: number | null) {
  return useQuery({
    queryKey: ["candidates", id],
    queryFn: () => candidatesApi.get(id as number),
    enabled: id !== null,
  });
}

export function useCreateCandidate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CandidateCreateInput) => candidatesApi.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}
