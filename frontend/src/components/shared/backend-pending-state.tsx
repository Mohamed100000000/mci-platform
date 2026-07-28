"use client";
import { motion } from "framer-motion";
import { type LucideIcon, Construction } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

interface BackendPendingStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  endpoints: string[];
}

export function BackendPendingState({ icon: Icon, title, description, endpoints }: BackendPendingStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex min-h-[60vh] items-center justify-center"
    >
      <Card className="max-w-lg border-dashed p-10 text-center">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary">
          <Icon className="h-6 w-6 text-primary" />
        </div>
        <div className="mb-3 flex items-center justify-center gap-2">
          <h2 className="text-lg font-semibold">{title}</h2>
          <Badge variant="warning" className="gap-1">
            <Construction className="h-3 w-3" /> Backend pending
          </Badge>
        </div>
        <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
        <div className="mt-6 rounded-lg border border-border bg-muted/40 p-4 text-left">
          <p className="mb-2 text-xs font-medium text-muted-foreground">Required API endpoints:</p>
          <ul className="space-y-1">
            {endpoints.map((e) => (
              <li key={e} className="font-mono text-xs text-foreground/80">{e}</li>
            ))}
          </ul>
        </div>
      </Card>
    </motion.div>
  );
}
