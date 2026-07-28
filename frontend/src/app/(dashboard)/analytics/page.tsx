"use client";
import { BarChart3 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function AnalyticsPage() {
  return (
    <>
      <PageHeader title="Analytics" description="Deep performance analytics and trend analysis." />
      <BackendPendingState
        icon={BarChart3}
        title="Advanced analytics"
        description="Question-level analytics, success-rate heatmaps, and MCI trend analysis across cohorts, companies, and time periods."
        endpoints={["GET /api/analytics/questions", "GET /api/analytics/trends", "GET /api/analytics/heatmap"]}
      />
    </>
  );
}
