"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { authApi, tokenStorage } from "@/lib/api/auth";
import type { User } from "@/types/mci";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refetchUser: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [loading, setLoading] = React.useState(true);
  const router = useRouter();

  const loadUser = React.useCallback(async () => {
    if (!tokenStorage.access) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await authApi.me();
      setUser(me);
    } catch {
      tokenStorage.clear();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    // Runs the initial "is there a valid session?" check against the
    // backend once on mount. setUser/setLoading happen inside the async
    // loadUser() body after the /users/me request resolves.
    // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional, one-time auth bootstrap
    void loadUser();
  }, [loadUser]);

  const login = React.useCallback(
    async (email: string, password: string) => {
      const token = await authApi.login(email, password);
      tokenStorage.set(token);
      const me = await authApi.me();
      setUser(me);
    },
    []
  );

  const logout = React.useCallback(() => {
    tokenStorage.clear();
    setUser(null);
    router.push("/login");
  }, [router]);

  const value = React.useMemo(
    () => ({ user, loading, login, logout, refetchUser: loadUser }),
    [user, loading, login, logout, loadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
