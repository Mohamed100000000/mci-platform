import { apiClient } from "./client";
import type { Trainee, TraineeCreateInput, TraineeUpdateInput } from "@/types/mci";

// Backend concept is "Trainee" (GET/POST /api/v1/trainees). The UI may still
// say "Candidates" in copy/labels, but this module is the real trainees API.
export const traineesApi = {
  list: async (): Promise<Trainee[]> => {
    const { data } = await apiClient.get<Trainee[]>("/api/v1/trainees");
    return data;
  },
  get: async (id: string): Promise<Trainee> => {
    const { data } = await apiClient.get<Trainee>(`/api/v1/trainees/${id}`);
    return data;
  },
  create: async (input: TraineeCreateInput): Promise<Trainee> => {
    const { data } = await apiClient.post<Trainee>("/api/v1/trainees", input);
    return data;
  },
  update: async (id: string, input: TraineeUpdateInput): Promise<Trainee> => {
    const { data } = await apiClient.patch<Trainee>(`/api/v1/trainees/${id}`, input);
    return data;
  },
};

export const organizationUnitsApi = {
  list: async () => {
    const { data } = await apiClient.get("/api/v1/organization-units");
    return data;
  },
  create: async (input: { name: string; unit_type?: string; imo_number?: string; contact_email?: string; contact_phone?: string }) => {
    const { data } = await apiClient.post("/api/v1/organization-units", input);
    return data;
  },
};
