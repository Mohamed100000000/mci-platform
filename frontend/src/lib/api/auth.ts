import { apiClient, API_BASE_URL } from "./client";
import type { Token, User } from "@/types/mci";

/**
 * IMPORTANT: POST /api/v1/auth/login uses FastAPI's OAuth2PasswordRequestForm,
 * which means the backend expects `application/x-www-form-urlencoded` with
 * fields named `username` (holds the email) and `password` — NOT a JSON
 * body with an `email` field. Sending JSON here will fail with a 422.
 */
export const authApi = {
  login: async (email: string, password: string): Promise<Token> => {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);
    const { data } = await apiClient.post<Token>("/api/v1/auth/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data;
  },

  /**
   * NOTE: the backend's /auth/refresh endpoint takes `refresh_token` as a
   * query parameter (Pydantic doesn't wrap it in a body model), so it must
   * be sent as `?refresh_token=...`, not as a JSON body.
   */
  refresh: async (refreshToken: string): Promise<Token> => {
    const { data } = await apiClient.post<Token>(
      `/api/v1/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`
    );
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await apiClient.get<User>("/api/v1/users/me");
    return data;
  },
};

const ACCESS_KEY = "mci_access_token";
const REFRESH_KEY = "mci_refresh_token";

export const tokenStorage = {
  get access(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(ACCESS_KEY);
  },
  get refresh(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_KEY);
  },
  set(token: Token) {
    window.localStorage.setItem(ACCESS_KEY, token.access_token);
    window.localStorage.setItem(REFRESH_KEY, token.refresh_token);
  },
  clear() {
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  },
};

export { API_BASE_URL };
