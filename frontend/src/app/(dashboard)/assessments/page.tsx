"use client";
import { ClipboardList } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function AssessmentsPage() {
  return (
    <>
      <PageHeader title="Assessments" description="Build and manage competency assessments." />
      <BackendPendingState
        icon={ClipboardList}
        title="Assessment builder"
        description="Create assessments with difficulty levels, passing scores, time limits, and category weighting, then assign them to candidates."
        endpoints={["POST /api/assessments", "GET /api/assessments", "POST /api/assessments/{id}/questions"]}
      />
    </>
  );
}
