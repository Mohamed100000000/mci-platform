"use client";
import { BookOpen } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable } from "@/components/shared/data-table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useCourses } from "@/hooks/use-courses";
import { courseColumns } from "./columns";
import { AddCourseDialog } from "./add-course-dialog";

export default function CoursesPage() {
  const { data, isLoading, isError, refetch } = useCourses();

  return (
    <>
      <PageHeader
        title="Courses"
        description="STCW-certified maritime training courses offered by your institute."
        actions={<AddCourseDialog />}
      />

      {isLoading ? (
        <div className="space-y-3">
          <Skeleton className="h-10 w-full max-w-xs" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
          <p className="text-sm text-muted-foreground">
            Could not load courses. Check that <code className="rounded bg-muted px-1">NEXT_PUBLIC_API_URL</code> points to a running backend.
          </p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>Retry</Button>
        </div>
      ) : (
        <DataTable
          columns={courseColumns}
          data={data || []}
          searchPlaceholder="Search courses by title or code..."
          emptyState={
            <div className="flex flex-col items-center gap-2 py-6">
              <BookOpen className="h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No courses yet.</p>
            </div>
          }
        />
      )}
    </>
  );
}
