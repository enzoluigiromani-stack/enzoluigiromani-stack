"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { useAuthStore } from "@/store/auth.store";
import { useUIStore } from "@/store/ui.store";
import { authService } from "@/services/auth.service";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token, user, setUser, logout, _hasHydrated } = useAuthStore();
  const { darkMode } = useUIStore();

  useEffect(() => {
    if (!_hasHydrated) return;
    if (!token) {
      router.push("/login");
      return;
    }
    if (!user) {
      authService.me().then(setUser).catch(() => {
        logout();
        router.push("/login");
      });
    }
  }, [token, user, router, setUser, logout, _hasHydrated]);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  if (!_hasHydrated) return null;
  if (!token) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
