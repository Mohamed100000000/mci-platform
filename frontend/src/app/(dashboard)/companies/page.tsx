"use client";
import { Building2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function CompaniesPage() {
  return (
    <>
      <PageHeader title="Companies" description="Manage shipping companies and their candidate rosters." />
      <BackendPendingState
        icon={Building2}
        title="Company management"
        description="This module will let institute admins manage client companies, assign candidates, and track per-company MCI performance."
        endpoints={["POST /api/companies", "GET /api/companies", "GET /api/companies/{id}/candidates"]}
      />
    </>
  );
}
