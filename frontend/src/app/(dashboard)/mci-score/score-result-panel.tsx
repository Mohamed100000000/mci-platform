"use client";
import * as React from "react";
import { toast } from "sonner";
import { Gauge } from "lucide-react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Tooltip as RechartsTooltip,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useComputeMci, useSavedMci } from "@/hooks/use-mci";

export function ScoreResultPanel({ candidateId }: { candidateId: number }) {
  const { data: mci, isLoading } = useSavedMci(candidateId);
  const computeMci = useComputeMci(candidateId);

  const handleCompute = () => {
    computeMci.mutate(undefined, {
      onSuccess: (data) => toast.success(`MCI computed: ${data.mci_score.toFixed(0)} (${data.level})`),
      onError: () => toast.error("Could not compute MCI. Save factor scores first."),
    });
  };

  const chartData = mci?.categories.map((c) => ({ label: c.label, value: c.sub_score_0_100 })) || [];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Marine Competency Index</CardTitle>
          <CardDescription>Computed from the factor scores on the left.</CardDescription>
        </div>
        <Button onClick={handleCompute} disabled={computeMci.isPending}>
          <Gauge className="h-4 w-4" />
          {computeMci.isPending ? "Computing..." : "Compute MCI"}
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? null : mci ? (
          <div className="grid gap-6 md:grid-cols-2 md:items-center">
            <div className="text-center md:text-left">
              <div className="text-6xl font-semibold text-primary">{mci.mci_score.toFixed(0)}</div>
              <Badge variant="accent" className="mt-2">{mci.level}</Badge>
              <p className="mt-3 text-xs text-muted-foreground">
                Profile completeness: {Math.round(mci.overall_completeness * 100)}%
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Last computed {new Date(mci.computed_at).toLocaleString()}
              </p>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={chartData} outerRadius="75%">
                <PolarGrid stroke="var(--border)" />
                <PolarAngleAxis dataKey="label" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 9 }} />
                <Radar dataKey="value" stroke="var(--brand-400)" fill="var(--brand-300)" fillOpacity={0.35} />
                <RechartsTooltip
                  contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <Gauge className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              No score yet. Save factor scores, then compute the MCI.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
