"use client";
import * as React from "react";
import { toast } from "sonner";
import { Save } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useFactorGroups, useLatestFactorScores, useSubmitFactorScores } from "@/hooks/use-mci";
import type { FactorScoreInput } from "@/lib/api/mci";

export function FactorScorePanel({
  candidateId,
  onSaved,
}: {
  candidateId: number;
  onSaved?: () => void;
}) {
  const { data: groups, isLoading: groupsLoading } = useFactorGroups();
  const { data: latest, isLoading: latestLoading } = useLatestFactorScores(candidateId);
  const submitScores = useSubmitFactorScores(candidateId);

  // Only locally-edited values live in state; anything not yet touched by
  // the user falls back to the fetched "latest" score (or 50) at render
  // time below -- this avoids syncing fetched data into state via an effect.
  const [edits, setEdits] = React.useState<Record<string, number>>({});

  const valueFor = (key: string) => edits[key] ?? latest?.[key] ?? 50;

  const setValue = (key: string, val: number) => {
    setEdits((prev) => ({ ...prev, [key]: val }));
  };

  const handleSave = () => {
    if (!groups) return;
    const allKeys = groups.flatMap((g) => g.factors.map((f) => f.key));
    const scores: FactorScoreInput[] = allKeys.map((key) => ({
      factor_key: key,
      raw_score: valueFor(key),
      evidence_type: "knowledge_only",
    }));
    submitScores.mutate(scores, {
      onSuccess: () => {
        toast.success(`Saved ${scores.length} factor scores.`);
        onSaved?.();
      },
      onError: () => toast.error("Could not save factor scores."),
    });
  };

  if (groupsLoading || latestLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-40 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {groups?.map((group) => (
        <Card key={group.key}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{group.label}</CardTitle>
              <Badge variant="outline">{Math.round(group.weight * 100)}% of MCI</Badge>
            </div>
            <CardDescription>Enter an evidence-backed score (0-100) for each factor.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {group.factors.map((factor) => {
              const value = valueFor(factor.key);
              return (
                <div key={factor.key}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span className="flex items-center gap-1.5 font-medium">
                      {factor.label}
                      {factor.optional && (
                        <span className="text-xs font-normal text-muted-foreground">(optional)</span>
                      )}
                    </span>
                    <span className="font-mono text-xs text-muted-foreground">{value}</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={value}
                    onChange={(e) => setValue(factor.key, Number(e.target.value))}
                    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary"
                  />
                </div>
              );
            })}
          </CardContent>
        </Card>
      ))}

      <Button onClick={handleSave} disabled={submitScores.isPending} className="w-full sm:w-auto">
        <Save className="h-4 w-4" />
        {submitScores.isPending ? "Saving..." : "Save factor scores"}
      </Button>
    </div>
  );
}
