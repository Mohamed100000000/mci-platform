"use client";
import Link from "next/link";
import { type ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Gauge, ExternalLink } from "lucide-react";

import type { Candidate } from "@/types/mci";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function initials(name: string) {
  return name.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase();
}

export const candidateColumns: ColumnDef<Candidate>[] = [
  {
    accessorKey: "full_name",
    header: "Candidate",
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <Avatar className="h-8 w-8">
          <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">
            {initials(row.original.full_name)}
          </AvatarFallback>
        </Avatar>
        <div>
          <p className="text-sm font-medium">{row.original.full_name}</p>
          <p className="text-xs text-muted-foreground">{row.original.nationality || "Nationality not set"}</p>
        </div>
      </div>
    ),
  },
  {
    accessorKey: "current_position",
    header: "Position",
    cell: ({ row }) => row.original.current_position || <span className="text-muted-foreground">—</span>,
  },
  {
    accessorKey: "years_of_experience",
    header: "Experience",
    cell: ({ row }) => `${row.original.years_of_experience} yrs`,
  },
  {
    accessorKey: "created_at",
    header: "Added",
    cell: ({ row }) => new Date(row.original.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => (
      <div className="flex justify-end">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/mci-score?candidate=${row.original.id}`}>
                <Gauge className="h-4 w-4" /> Score MCI
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link href={`/candidates/${row.original.id}`}>
                <ExternalLink className="h-4 w-4" /> View profile
              </Link>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    ),
  },
];
