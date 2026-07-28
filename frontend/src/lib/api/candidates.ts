import { apiClient } from "./client";
import type { Candidate, CandidateCreateInput } from "@/types/mci";

export const candidatesApi = {
  list: async (): Promise<Candidate[]> => {
    const { data } = await apiClient.get<Candidate[]>("/api/users");
    return data;
  },
  get: async (id: number): Promise<Candidate> => {
    const { data } = await apiClient.get<Candidate>(`/api/users/${id}`);
    return data;
  },
  create: async (input: CandidateCreateInput): Promise<Candidate> => {
    const { data } = await apiClient.post<Candidate>("/api/users", input);
    return data;
  },
};
