"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./auth-context";

/**
 * Wrap any (dashboard) layout content in this to require an authenticated
 * session. Redirects to /login if there's no valid user once the initial
 * /users/me check has finished.
 */
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">
        Checking your session…
      </div>
    );
  }

  if (!user) return null;

  return <>{children}</>;
}
