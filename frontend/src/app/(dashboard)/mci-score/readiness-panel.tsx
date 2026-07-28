"use client";
import * as React from "react";
import { Target, CheckCircle2, AlertTriangle } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { usePositions, useReadiness, useSkillGap } from "@/hooks/use-positions";

const VERDICT_STYLES: Record<string, { variant: "success" | "warning" | "danger" | "secondary"; icon: React.ElementType }> = {
  Ready: { variant: "success", icon: CheckCircle2 },
  "Almost Ready": { variant: "warning", icon: Target },
  "Needs Improvement": { variant: "warning", icon: AlertTriangle },
  "Not Qualified Yet": { variant: "danger", icon: AlertTriangle },
};

const PRIORITY_VARIANT: Record<string, "danger" | "warning" | "success"> = {
  High: "danger",
  Medium: "warning",
  Low: "success",
};

export function ReadinessPanel({ candidateId }: { candidateId: number }) {
  const { data: positions, isLoading: positionsLoading } = usePositions();
  const [selectedPositionId, setSelectedPositionId] = React.useState<number | null>(null);

  // Derive the effective position directly during render instead of
  // syncing it via an effect: falls back to the first loaded position
  // until the user explicitly picks one.
  const positionId = selectedPositionId ?? positions?.[0]?.id ?? null;

  const { data: readiness, isLoading: readinessLoading } = useReadiness(candidateId, positionId);
  const { data: skillGap, isLoading: gapLoading } = useSkillGap(candidateId, positionId);

  const verdictStyle = readiness ? VERDICT_STYLES[readiness.verdict] : undefined;
  const VerdictIcon = verdictStyle?.icon ?? Target;

  return (
    <Card>
      <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <CardTitle>Job Readiness &amp; Skill Gap</CardTitle>
          <CardDescription>Compare this candidate against a target position.</CardDescription>
        </div>
        {positionsLoading ? (
          <Skeleton className="h-9 w-56" />
        ) : (
          <Select
            value={positionId ? String(positionId) : undefined}
            onValueChange={(v) => setSelectedPositionId(Number(v))}
          >
            <SelectTrigger className="w-full sm:w-64">
              <SelectValue placeholder="Select a position" />
            </SelectTrigger>
            <SelectContent>
              {positions?.map((p) => (
                <SelectItem key={p.id} value={String(p.id)}>{p.position_title}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </CardHeader>
      <CardContent>
        {readinessLoading || gapLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : readiness ? (
          <>
            <div className="mb-5 flex flex-wrap items-center gap-3">
              <Badge variant={verdictStyle?.variant} className="gap-1.5 px-3 py-1 text-sm">
                <VerdictIcon className="h-3.5 w-3.5" />
                {readiness.verdict}
              </Badge>
              <span className="text-sm text-muted-foreground">
                MCI {readiness.mci_score.toFixed(0)} &middot; position requires &ge; {readiness.min_overall_mci}
              </span>
            </div>

            {skillGap && skillGap.items.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Priority</TableHead>
                    <TableHead>Factor</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Current &rarr; Required</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {skillGap.items.map((item) => (
                    <TableRow key={item.factor_key}>
                      <TableCell>
                        <Badge variant={PRIORITY_VARIANT[item.priority]}>{item.priority}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{item.factor_label}</TableCell>
                      <TableCell className="text-muted-foreground">{item.category}</TableCell>
                      <TableCell className="text-right font-mono text-xs">
                        {item.actual} &rarr; {item.required}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="rounded-lg bg-success/10 px-4 py-3 text-sm text-success">
                All requirements met for this position &mdash; no skill gaps.
              </p>
            )}
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Select a position to check readiness.</p>
        )}
      </CardContent>
    </Card>
  );
}
