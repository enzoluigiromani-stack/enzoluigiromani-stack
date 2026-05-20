"use client";

import { useState } from "react";
import { Settings2, Kanban, Users, Plug, ShieldCheck, User, Lock } from "lucide-react";
import { GeneralSection } from "@/components/settings/general-section";
import { PipelineSection } from "@/components/settings/pipeline-section";
import { TeamSection } from "@/components/settings/team-section";
import { SecuritySection } from "@/components/settings/security-section";
import { IntegrationsSection } from "@/components/settings/integrations-section";
import { AccountSection } from "@/components/settings/account-section";
import { useAuthStore } from "@/store/auth.store";
import { cn } from "@/lib/utils";

type Tab = "geral" | "pipeline" | "equipe" | "integracoes" | "seguranca" | "conta";

const TABS: {
  id: Tab;
  label: string;
  icon: React.ElementType;
  adminOnly?: boolean;
}[] = [
  { id: "geral",       label: "Geral",        icon: Settings2,   adminOnly: true },
  { id: "pipeline",    label: "Pipeline",     icon: Kanban,      adminOnly: true },
  { id: "equipe",      label: "Equipe",       icon: Users,       adminOnly: true },
  { id: "integracoes", label: "Integrações",  icon: Plug,        adminOnly: true },
  { id: "seguranca",   label: "Segurança",    icon: ShieldCheck },
  { id: "conta",       label: "Minha conta",  icon: User },
];

export default function SettingsPage() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin" || user?.role === "manager";

  const [activeTab, setActiveTab] = useState<Tab>(isAdmin ? "geral" : "seguranca");

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Configurações</h1>
        <p className="text-muted-foreground">Gerencie o workspace e suas preferências</p>
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

        {/* Conteúdo da tab */}
        <div className="flex-1 min-w-0">
          {activeTab === "geral" && (isAdmin ? <GeneralSection /> : <AdminOnlyMessage />)}
          {activeTab === "pipeline" && (isAdmin ? <PipelineSection /> : <AdminOnlyMessage />)}
          {activeTab === "equipe" && (isAdmin ? <TeamSection /> : <AdminOnlyMessage />)}
          {activeTab === "integracoes" && (isAdmin ? <IntegrationsSection /> : <AdminOnlyMessage />)}
          {activeTab === "seguranca" && <SecuritySection />}
          {activeTab === "conta" && <AccountSection />}
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
