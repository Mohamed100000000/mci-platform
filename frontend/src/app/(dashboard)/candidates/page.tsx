"use client";
import { Users } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable } from "@/components/shared/data-table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useCandidates } from "@/hooks/use-candidates";
import { candidateColumns } from "./columns";
import { AddCandidateDialog } from "./add-candidate-dialog";

export default function CandidatesPage() {
  const { data, isLoading, isError, refetch } = useCandidates();

  return (
    <>
      <PageHeader
        title="Candidates"
        description="Manage maritime professional profiles and their competency scores."
        actions={<AddCandidateDialog />}
      />

      {isLoading ? (
        <div className="space-y-3">
          <Skeleton className="h-10 w-full max-w-xs" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
          <p className="text-sm text-muted-foreground">
            Could not load candidates. Check that <code className="rounded bg-muted px-1">NEXT_PUBLIC_API_URL</code> points to a running backend.
          </p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>Retry</Button>
        </div>
      ) : (
        <DataTable
          columns={candidateColumns}
          data={data || []}
          searchPlaceholder="Search candidates by name..."
          emptyState={
            <div className="flex flex-col items-center gap-2 py-6">
              <Users className="h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No candidates yet.</p>
            </div>
          }
        />
      )}
    </>
  );
}
