"use client";
import { PlayCircle } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function SessionsPage() {
  return (
    <>
      <PageHeader title="Assessment Sessions" description="Monitor live and completed assessment sessions." />
      <BackendPendingState
        icon={PlayCircle}
        title="Live session monitoring"
        description="Track candidates currently taking assessments and review completed session results in real time."
        endpoints={["GET /api/sessions", "GET /api/sessions/{id}", "WS /ws/sessions/{id}"]}
      />
    </>
  );
}
