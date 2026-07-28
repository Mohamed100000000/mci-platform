"use client";

import * as React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { ChevronsLeft, Lock, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";
import { navSections } from "./nav-config";
import { useSidebar } from "./sidebar-context";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export function Sidebar() {
  const { collapsed, toggle, mobileOpen, setMobileOpen } = useSidebar();
  const pathname = usePathname();

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <motion.aside
        animate={{ width: collapsed ? 76 : 264 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground",
          "lg:translate-x-0 transition-transform duration-200",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className="flex h-16 shrink-0 items-center gap-3 border-b border-sidebar-border px-4">
          <Link href="/dashboard" className="flex items-center gap-3 overflow-hidden">
            <div className="relative h-9 w-9 shrink-0 overflow-hidden rounded-lg">
              <Image src="/logo-mark-square.png" alt="MCI Platform" fill className="object-cover" priority />
            </div>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="flex flex-col leading-none overflow-hidden whitespace-nowrap"
              >
                <span className="text-sm font-semibold tracking-wide">
                  MCI <span className="text-brand-300">Platform</span>
                </span>
                <span className="text-[10px] text-sidebar-muted mt-0.5">
                  Maritime Competency Index
                </span>
              </motion.div>
            )}
          </Link>
        </div>

        {/* Nav */}
        <TooltipProvider delayDuration={0}>
          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
            {navSections.map((section) => (
              <div key={section.title}>
                {!collapsed && (
                  <p className="px-2 mb-2 text-[10px] font-semibold uppercase tracking-wider text-sidebar-muted">
                    {section.title}
                  </p>
                )}
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const active = pathname === item.href || pathname?.startsWith(item.href + "/");
                    const Icon = item.icon;

                    const linkContent = (
                      <Link
                        href={item.href}
                        onClick={() => setMobileOpen(false)}
                        className={cn(
                          "group relative flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
                          active
                            ? "bg-sidebar-accent text-white"
                            : "text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-white"
                        )}
                      >
                        {active && (
                          <motion.span
                            layoutId="active-nav-pill"
                            className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-full bg-brand-300"
                          />
                        )}
                        <Icon className={cn("h-[18px] w-[18px] shrink-0", active && "text-brand-300")} />
                        {!collapsed && (
                          <span className="flex-1 truncate">{item.label}</span>
                        )}
                        {!collapsed && !item.backendReady && (
                          <Lock className="h-3 w-3 text-sidebar-muted shrink-0" />
                        )}
                      </Link>
                    );

                    if (collapsed) {
                      return (
                        <Tooltip key={item.href}>
                          <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                          <TooltipContent side="right" className="flex items-center gap-1.5">
                            {item.label}
                            {!item.backendReady && <Lock className="h-3 w-3" />}
                          </TooltipContent>
                        </Tooltip>
                      );
                    }
                    return <React.Fragment key={item.href}>{linkContent}</React.Fragment>;
                  })}
                </div>
              </div>
            ))}
          </nav>
        </TooltipProvider>

        {/* Footer */}
        <div className="border-t border-sidebar-border p-3">
          {!collapsed && (
            <div className="mb-2 flex items-center gap-2 rounded-lg bg-sidebar-accent px-3 py-2 text-xs text-sidebar-muted">
              <Sparkles className="h-3.5 w-3.5 text-brand-300 shrink-0" />
              <span>Phase 1 MVP &mdash; more modules launching soon</span>
            </div>
          )}
          <button
            onClick={toggle}
            className="flex w-full items-center justify-center gap-2 rounded-lg py-2 text-sidebar-muted hover:bg-sidebar-accent hover:text-white transition-colors"
          >
            <ChevronsLeft className={cn("h-4 w-4 transition-transform", collapsed && "rotate-180")} />
            {!collapsed && <span className="text-xs font-medium">Collapse</span>}
          </button>
        </div>
      </motion.aside>
    </>
  );
}
