"use client";
import Link from "next/link";
import { type ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Gauge, ExternalLink } from "lucide-react";

import type { Trainee } from "@/types/mci";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function initials(name: string) {
  return name.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase();
}

export const candidateColumns: ColumnDef<Trainee>[] = [
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
    accessorKey: "rank",
    header: "Rank",
    cell: ({ row }) => row.original.rank || <span className="text-muted-foreground">—</span>,
  },
  {
    accessorKey: "trainee_code",
    header: "Trainee Code",
    cell: ({ row }) => <span className="font-mono text-xs">{row.original.trainee_code}</span>,
  },
  {
    accessorKey: "email",
    header: "Contact",
    cell: ({ row }) => row.original.email || row.original.phone || <span className="text-muted-foreground">—</span>,
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
