import { apiClient } from "./client";
import type { Course, CourseCreateInput, CourseSession, CourseSessionCreateInput } from "@/types/mci";

export const coursesApi = {
  list: async (): Promise<Course[]> => {
    const { data } = await apiClient.get<Course[]>("/api/v1/courses");
    return data;
  },
  get: async (id: string): Promise<Course> => {
    const { data } = await apiClient.get<Course>(`/api/v1/courses/${id}`);
    return data;
  },
  create: async (input: CourseCreateInput): Promise<Course> => {
    const { data } = await apiClient.post<Course>("/api/v1/courses", input);
    return data;
  },
  listSessions: async (courseId: string): Promise<CourseSession[]> => {
    const { data } = await apiClient.get<CourseSession[]>(`/api/v1/courses/${courseId}/sessions`);
    return data;
  },
  createSession: async (input: CourseSessionCreateInput): Promise<CourseSession> => {
    const { data } = await apiClient.post<CourseSession>("/api/v1/courses/sessions", input);
    return data;
  },
};
