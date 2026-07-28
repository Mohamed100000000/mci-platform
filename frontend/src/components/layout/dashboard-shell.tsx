"use client";
import * as React from "react";
import { motion } from "framer-motion";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";
import { useSidebar } from "./sidebar-context";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const { collapsed } = useSidebar();

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <motion.div
        animate={{ marginLeft: collapsed ? 76 : 264 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="hidden lg:block"
      >
        <Topbar />
        <main className="p-4 sm:p-6 lg:p-8">{children}</main>
      </motion.div>
      <div className="lg:hidden">
        <Topbar />
        <main className="p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
