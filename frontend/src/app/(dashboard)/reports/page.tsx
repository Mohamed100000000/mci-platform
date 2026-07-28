"use client";
import { FileBarChart } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function ReportsPage() {
  return (
    <>
      <PageHeader title="Reports" description="Company, candidate, and assessment reports." />
      <BackendPendingState
        icon={FileBarChart}
        title="Report exports"
        description="Generate Excel and PDF reports for companies, candidates, and assessments — mirrors the reporting patterns already built for the AZDA certificate system."
        endpoints={["GET /api/reports/companies/{id}", "GET /api/reports/candidates/{id}", "GET /api/reports/export?format=xlsx"]}
      />
    </>
  );
}
