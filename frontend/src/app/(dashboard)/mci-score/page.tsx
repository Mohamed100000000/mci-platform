"use client";
import * as React from "react";
import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Users } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCandidates } from "@/hooks/use-candidates";
import { FactorScorePanel } from "./factor-score-panel";
import { ScoreResultPanel } from "./score-result-panel";
import { ReadinessPanel } from "./readiness-panel";

function MciScoreContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: candidates, isLoading } = useCandidates();

  const candidateParam = searchParams.get("candidate");
  const [selectedCandidateId, setSelectedCandidateId] = React.useState<number | null>(
    candidateParam ? Number(candidateParam) : null
  );

  const candidateId = selectedCandidateId ?? candidates?.[0]?.id ?? null;

  const handleSelect = (value: string) => {
    const id = Number(value);
    setSelectedCandidateId(id);
    router.replace(`/mci-score?candidate=${id}`);
  };

  return (
    <>
      <PageHeader
        title="MCI Score"
        description="Enter competency evidence, compute the Marine Competency Index, and check job readiness."
        actions={
          isLoading ? (
            <Skeleton className="h-9 w-56" />
          ) : candidates && candidates.length > 0 ? (
            <Select value={candidateId ? String(candidateId) : undefined} onValueChange={handleSelect}>
              <SelectTrigger className="w-64">
                <Users className="h-4 w-4 opacity-50" />
                <SelectValue placeholder="Select a candidate" />
              </SelectTrigger>
              <SelectContent>
                {candidates.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>{c.full_name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : null
        }
      />

      {isLoading ? (
        <Skeleton className="h-96 w-full rounded-xl" />
      ) : !candidateId ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
          <Users className="h-8 w-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            No candidates yet. Create one from the Candidates page first.
          </p>
        </div>
      ) : (
        <Tabs defaultValue="factors">
          <TabsList>
            <TabsTrigger value="factors">Factor Scores</TabsTrigger>
            <TabsTrigger value="score">MCI Score</TabsTrigger>
            <TabsTrigger value="readiness">Job Readiness</TabsTrigger>
          </TabsList>

          <TabsContent value="factors">
            <FactorScorePanel candidateId={candidateId} />
          </TabsContent>
          <TabsContent value="score">
            <ScoreResultPanel candidateId={candidateId} />
          </TabsContent>
          <TabsContent value="readiness">
            <ReadinessPanel candidateId={candidateId} />
          </TabsContent>
        </Tabs>
      )}
    </>
  );
}

export default function MciScorePage() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full rounded-xl" />}>
      <MciScoreContent />
    </Suspense>
  );
}
