"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Users, Gauge, Award, TrendingUp, ArrowUpRight, ArrowRight,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";

import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useDashboardStats } from "@/hooks/use-dashboard-stats";

const LEVEL_COLORS: Record<string, string> = {
  "Entry Level": "#93A5C4",
  "Developing Professional": "#6AABE9",
  "Competent Professional": "#3A72BE",
  "Senior Professional": "#154482",
  Expert: "#0A2750",
  "Elite Maritime Professional": "#04102A",
};

function KpiCard({
  icon: Icon, label, value, delta, deltaLabel, index,
}: {
  icon: React.ElementType; label: string; value: string; delta?: string; deltaLabel?: string; index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
    >
      <Card className="relative overflow-hidden">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium text-muted-foreground">{label}</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
              {delta && (
                <div className="mt-2 flex items-center gap-1 text-xs font-medium text-success">
                  <ArrowUpRight className="h-3.5 w-3.5" />
                  {delta} <span className="font-normal text-muted-foreground">{deltaLabel}</span>
                </div>
              )}
            </div>
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary">
              <Icon className="h-5 w-5 text-primary" />
            </span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { data, isLoading } = useDashboardStats();

  const levelData = data
    ? Object.entries(data.levelCounts).map(([level, count]) => ({ level, count }))
    : [];

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Executive overview of candidate competency across your organization."
        actions={
          <Button asChild>
            <Link href="/candidates">
              <Users className="h-4 w-4" /> New candidate
            </Link>
          </Button>
        }
      />

      {/* KPI cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32 rounded-xl" />)
        ) : (
          <>
            <KpiCard icon={Users} label="Total Candidates" value={String(data?.totalCandidates ?? 0)} index={0} />
            <KpiCard
              icon={Gauge}
              label="Average MCI Score"
              value={data?.averageMci ? data.averageMci.toFixed(0) : "—"}
              index={1}
            />
            <KpiCard
              icon={TrendingUp}
              label="Profiles Scored"
              value={`${data?.scoredCandidates ?? 0} / ${data?.totalCandidates ?? 0}`}
              index={2}
            />
            <KpiCard icon={Award} label="Certificates Issued" value="—" index={3} />
          </>
        )}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        {/* Category breakdown */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Average competency by category</CardTitle>
            <CardDescription>Mean sub-score (0-100) across all scored candidates.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-72 w-full" />
            ) : data && data.categoryAverages.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.categoryAverages} layout="vertical" margin={{ left: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} stroke="var(--muted-foreground)" fontSize={12} />
                  <YAxis
                    type="category"
                    dataKey="label"
                    stroke="var(--muted-foreground)"
                    fontSize={12}
                    width={160}
                  />
                  <RechartsTooltip
                    contentStyle={{
                      background: "var(--card)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="value" fill="var(--brand-400)" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-72 flex-col items-center justify-center text-center text-sm text-muted-foreground">
                No MCI scores computed yet.
                <Link href="/mci-score" className="mt-2 flex items-center gap-1 font-medium text-primary hover:underline">
                  Compute a score <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Level distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Competency levels</CardTitle>
            <CardDescription>Distribution of scored candidates.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-56 w-full rounded-full" />
            ) : levelData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={levelData} dataKey="count" nameKey="level" innerRadius={50} outerRadius={80} paddingAngle={2}>
                    {levelData.map((entry) => (
                      <Cell key={entry.level} fill={LEVEL_COLORS[entry.level] || "var(--brand-400)"} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-56 items-center justify-center text-center text-sm text-muted-foreground">
                No data yet
              </div>
            )}
            <div className="mt-2 space-y-1.5">
              {levelData.map((l) => (
                <div key={l.level} className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full" style={{ background: LEVEL_COLORS[l.level] }} />
                    {l.level}
                  </span>
                  <span className="font-medium">{l.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent candidates */}
      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent candidates</CardTitle>
            <CardDescription>Latest profiles added to the platform.</CardDescription>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/candidates">
              View all <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent className="space-y-1">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 w-full rounded-lg" />)
          ) : data && data.candidates.length > 0 ? (
            data.candidates.slice(0, 5).map((c) => {
              const mci = data.mciByUser[c.id];
              return (
                <div key={c.id} className="flex items-center gap-3 rounded-lg px-2 py-2.5 hover:bg-muted/50">
                  <Avatar className="h-9 w-9">
                    <AvatarFallback className="bg-secondary text-secondary-foreground">
                      {c.full_name.split(" ").map((n) => n[0]).slice(0, 2).join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{c.full_name}</p>
                    <p className="truncate text-xs text-muted-foreground">
                      {c.current_position || "Position not set"} &middot; {c.nationality || "—"}
                    </p>
                  </div>
                  {mci ? (
                    <Badge variant="accent">{mci.mci_score.toFixed(0)} MCI</Badge>
                  ) : (
                    <Badge variant="outline">Not scored</Badge>
                  )}
                </div>
              );
            })
          ) : (
            <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
              <p className="text-sm text-muted-foreground">No candidates yet.</p>
              <Button size="sm" asChild>
                <Link href="/candidates">Create your first candidate</Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
}
