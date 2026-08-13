"use client";
import { Gauge } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function MciScorePage() {
  return (
    <>
      <PageHeader
        title="MCI Score"
        description="Compute and review the Marine Competency Index for a trainee."
      />
      <BackendPendingState
        icon={Gauge}
        title="MCI factor scoring & job readiness"
        description="Enter competency evidence, compute the Marine Competency Index, and check job readiness against target positions. This panel previously called endpoints that don't exist on the real backend and used numeric candidate IDs incompatible with the real Trainee model — it needs a proper real implementation as its own reviewed piece of work, not folded into this build fix."
        endpoints={["POST /api/v1/mci/trainees/{id}/calculate", "GET /api/v1/mci/trainees/{id}/latest", "GET /api/v1/mci/trainees/{id}/history"]}
      />
    </>
  );
}
