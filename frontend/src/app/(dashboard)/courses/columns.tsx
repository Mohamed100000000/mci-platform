"use client";
import type { ColumnDef } from "@tanstack/react-table";
import { BookOpen } from "lucide-react";

import type { Course } from "@/types/mci";
import { Badge } from "@/components/ui/badge";

export const courseColumns: ColumnDef<Course>[] = [
  {
    accessorKey: "title",
    header: "Course",
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary">
          <BookOpen className="h-4 w-4 text-primary" />
        </span>
        <div>
          <p className="text-sm font-medium">{row.original.title}</p>
          <p className="text-xs text-muted-foreground">{row.original.stcw_reference || "No STCW reference"}</p>
        </div>
      </div>
    ),
  },
  {
    accessorKey: "code",
    header: "Code",
    cell: ({ row }) => <span className="font-mono text-xs">{row.original.code}</span>,
  },
  {
    accessorKey: "duration_hours",
    header: "Duration",
    cell: ({ row }) => <span className="text-sm">{row.original.duration_hours} hrs</span>,
  },
  {
    accessorKey: "validity_months",
    header: "Validity",
    cell: ({ row }) =>
      row.original.validity_months ? (
        <span className="text-sm">{row.original.validity_months} mo</span>
      ) : (
        <span className="text-muted-foreground">—</span>
      ),
  },
  {
    accessorKey: "max_capacity",
    header: "Capacity",
    cell: ({ row }) => <Badge variant="outline">{row.original.max_capacity}</Badge>,
  },
];
