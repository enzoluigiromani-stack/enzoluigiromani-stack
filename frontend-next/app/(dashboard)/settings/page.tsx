"use client";

import { useState } from "react";
import { Settings2, Kanban, Users, Plug, ShieldCheck, User, Lock, Palette, RefreshCw, WifiOff } from "lucide-react";
import { GeneralSection } from "@/components/settings/general-section";
import { PipelineSection } from "@/components/settings/pipeline-section";
import { TeamSection } from "@/components/settings/team-section";
import { SecuritySection } from "@/components/settings/security-section";
import { IntegrationsSection } from "@/components/settings/integrations-section";
import { AccountSection } from "@/components/settings/account-section";
import { AppearanceSection } from "@/components/settings/appearance-section";
import { useAuthStore } from "@/store/auth.store";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import { cn } from "@/lib/utils";

function LiveBadge() {
  const status = useRealtimeStatus();
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full border transition-all",
      status === "connected"
        ? "text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/20"
        : status === "connecting"
        ? "text-amber-500 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20"
        : "text-muted-foreground border-border bg-muted/40",
    )}>
      {status === "connected" ? (
        <>
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-60" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
          </span>
          Ao vivo
        </>
      ) : status === "connecting" ? (
        <><RefreshCw className="h-3 w-3 animate-spin" /> Conectando…</>
      ) : (
        <><WifiOff className="h-3 w-3" /> Offline</>
      )}
    </span>
  );
}

type Tab = "geral" | "pipeline" | "equipe" | "integracoes" | "seguranca" | "aparencia" | "conta";

const TABS: {
  id: Tab;
  label: string;
  icon: React.ElementType;
  adminOnly?: boolean;
}[] = [
  { id: "geral",       label: "Geral",        icon: Settings2, adminOnly: true },
  { id: "pipeline",    label: "Pipeline",     icon: Kanban,    adminOnly: true },
  { id: "equipe",      label: "Equipe",       icon: Users,     adminOnly: true },
  { id: "integracoes", label: "Integrações",  icon: Plug,      adminOnly: true },
  { id: "seguranca",   label: "Segurança",    icon: ShieldCheck },
  { id: "aparencia",   label: "Aparência",    icon: Palette },
  { id: "conta",       label: "Minha conta",  icon: User },
];

export default function SettingsPage() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin" || user?.role === "manager";

  const [activeTab, setActiveTab] = useState<Tab>(isAdmin ? "geral" : "seguranca");

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Configurações</h1>
          <p className="text-muted-foreground">Gerencie o workspace e suas preferências</p>
        </div>
        <LiveBadge />
      </div>

      <div className="flex gap-6">
        {/* Sidebar de navegação */}
        <nav className="w-44 shrink-0 space-y-0.5">
          {TABS.map(({ id, label, icon: Icon, adminOnly }) => {
            const locked = adminOnly && !isAdmin;
            const active = activeTab === id;

            return (
              <button
                key={id}
                onClick={() => !locked && setActiveTab(id)}
                disabled={locked}
                className={cn(
                  "w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left",
                  active
                    ? "bg-primary text-primary-foreground"
                    : locked
                    ? "text-muted-foreground/40 cursor-not-allowed"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="flex-1 truncate">{label}</span>
                {locked && <Lock className="h-3 w-3 shrink-0 opacity-50" />}
              </button>
            );
          })}
        </nav>

        {/* Conteúdo */}
        <div className="flex-1 min-w-0">
          {activeTab === "geral"       && (isAdmin ? <GeneralSection />       : <AdminOnlyMessage />)}
          {activeTab === "pipeline"    && (isAdmin ? <PipelineSection />    : <AdminOnlyMessage />)}
          {activeTab === "equipe"      && (isAdmin ? <TeamSection />         : <AdminOnlyMessage />)}
          {activeTab === "integracoes" && (isAdmin ? <IntegrationsSection /> : <AdminOnlyMessage />)}
          {activeTab === "seguranca"   && <SecuritySection />}
          {activeTab === "aparencia"   && <AppearanceSection />}
          {activeTab === "conta"       && <AccountSection />}
        </div>
      </div>
    </div>
  );
}

function AdminOnlyMessage() {
  return (
    <div className="flex flex-col items-center justify-center h-48 gap-3 border-2 border-dashed border-border rounded-xl">
      <Lock className="h-8 w-8 text-muted-foreground/40" />
      <p className="text-muted-foreground font-medium">Acesso restrito</p>
      <p className="text-sm text-muted-foreground">
        Apenas administradores podem alterar essas configurações
      </p>
    </div>
  );
}
