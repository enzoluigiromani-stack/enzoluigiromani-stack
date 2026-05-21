import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setToken: (token) => {
        set({ token });
        if (typeof window !== "undefined") localStorage.setItem("crm_token", token);
      },
      setUser: (user) => set({ user }),
      logout: () => {
        set({ token: null, user: null });
        if (typeof window !== "undefined") localStorage.removeItem("crm_token");
      },
    }),
    { name: "crm-auth" }
  )
);
