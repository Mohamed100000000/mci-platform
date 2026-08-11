"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { coursesApi } from "@/lib/api/courses";
import type { CourseCreateInput } from "@/types/mci";

export function useCourses() {
  return useQuery({ queryKey: ["courses"], queryFn: coursesApi.list });
}

export function useCourse(id: string | null) {
  return useQuery({
    queryKey: ["courses", id],
    queryFn: () => coursesApi.get(id as string),
    enabled: id !== null,
  });
}

export function useCreateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CourseCreateInput) => coursesApi.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useCourseSessions(courseId: string | null) {
  return useQuery({
    queryKey: ["courses", courseId, "sessions"],
    queryFn: () => coursesApi.listSessions(courseId as string),
    enabled: courseId !== null,
  });
}
