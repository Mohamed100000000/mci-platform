"use client";
import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Gauge, MapPin, Briefcase, Hash } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useCandidate } from "@/hooks/use-candidates";
import { useLatestMci } from "@/hooks/use-mci";

export default function CandidateDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const { data: candidate, isLoading } = useCandidate(id);
  const { data: mci, isLoading: mciLoading } = useLatestMci(id);

  if (isLoading) {
    return <Skeleton className="h-96 w-full rounded-xl" />;
  }
  if (!candidate) {
    return <p className="text-sm text-muted-foreground">Candidate not found.</p>;
  }

  const initials = candidate.full_name.split(" ").map((n) => n[0]).slice(0, 2).join("");

  const components = mci
    ? [
        { label: "Attendance", value: mci.attendance_component },
        { label: "Competency", value: mci.competency_component },
        { label: "Certification", value: mci.certification_component },
        { label: "Recency", value: mci.recency_component },
      ]
    : [];

  return (
    <>
      <Link href="/candidates" className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to candidates
      </Link>

      <PageHeader
        title={candidate.full_name}
        description="Candidate profile and competency overview."
        actions={
          <Button asChild>
            <Link href={`/mci-score?candidate=${candidate.id}`}>
              <Gauge className="h-4 w-4" /> {mci ? "Update MCI score" : "Compute MCI score"}
            </Link>
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center pt-6 text-center">
            <Avatar className="h-20 w-20 border border-border">
              <AvatarFallback className="bg-primary text-primary-foreground text-xl">{initials}</AvatarFallback>
            </Avatar>
            <h2 className="mt-4 text-lg font-semibold">{candidate.full_name}</h2>
            <p className="text-sm text-muted-foreground">{candidate.rank || "Rank not set"}</p>

            <div className="mt-5 w-full space-y-3 text-left text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <MapPin className="h-4 w-4" /> {candidate.nationality || "Not specified"}
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Briefcase className="h-4 w-4" /> {candidate.rank || "Not specified"}
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Hash className="h-4 w-4" /> {candidate.trainee_code}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Marine Competency Index</CardTitle>
            <CardDescription>Latest computed score and component breakdown.</CardDescription>
          </CardHeader>
          <CardContent>
            {mciLoading ? (
              <Skeleton className="h-48 w-full" />
            ) : mci ? (
              <div>
                <div className="mb-6 flex items-center gap-6">
                  <div className="text-5xl font-semibold text-primary">{mci.total_score.toFixed(0)}</div>
                  <div>
                    <Badge variant="accent">out of 1000</Badge>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Calculated on {new Date(mci.calculated_on).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="space-y-3">
                  {components.map((c) => (
                    <div key={c.label}>
                      <div className="mb-1 flex justify-between text-xs">
                        <span className="font-medium">{c.label}</span>
                        <span className="text-muted-foreground">{c.value.toFixed(0)}</span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${Math.min(100, c.value)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3 py-10 text-center">
                <Gauge className="h-8 w-8 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No MCI score computed yet for this candidate.</p>
                <Button asChild size="sm">
                  <Link href={`/mci-score?candidate=${candidate.id}`}>Compute now</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
