"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Users,
  MessageSquare,
  CheckSquare,
  AlertCircle,
  TrendingUp,
  UserPlus,
  ArrowRight,
  ListChecks,
  Inbox,
  WifiOff,
  RefreshCw,
  Activity,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { MetricsCard } from "@/components/dashboard/metrics-card";
import { KanbanBoard } from "@/components/dashboard/kanban-board";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { leadsService } from "@/services/leads.service";
import { api } from "@/services/api";
import { useActivityFeed, type FeedEvent } from "@/hooks/use-activity-feed";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import { cn } from "@/lib/utils";
import type { TaskSummary, KanbanColumn } from "@/types";

// ── Data hooks ────────────────────────────────────────────────────────────────

function useBoard() {
  return useQuery<KanbanColumn[]>({
    queryKey: ["board"],
    queryFn: leadsService.getBoard,
    staleTime: 30_000,
  });
}

function useTaskSummary() {
  return useQuery<TaskSummary>({
    queryKey: ["task-summary"],
    queryFn: async () => {
      const { data } = await api.get<TaskSummary>("/tasks/summary");
      return data;
    },
    staleTime: 30_000,
  });
}

function useLeads() {
  return useQuery({
    queryKey: ["leads"],
    queryFn: leadsService.getLeads,
    staleTime: 30_000,
  });
}

// ── Live status badge ─────────────────────────────────────────────────────────

function LiveBadge() {
  const status = useRealtimeStatus();
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full border transition-all",
        status === "connected"
          ? "text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/20"
          : status === "connecting"
          ? "text-amber-500 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20"
          : "text-muted-foreground border-border bg-muted/40",
      )}
    >
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

// ── Feed event icon + color ───────────────────────────────────────────────────

const FEED_META: Record<FeedEvent["type"], { icon: React.ElementType; color: string }> = {
  lead_created:    { icon: UserPlus,    color: "text-blue-500 bg-blue-50 dark:bg-blue-900/20" },
  lead_moved:      { icon: ArrowRight,  color: "text-violet-500 bg-violet-50 dark:bg-violet-900/20" },
  task_created:    { icon: ListChecks,  color: "text-amber-500 bg-amber-50 dark:bg-amber-900/20" },
  message_sent:    { icon: MessageSquare, color: "text-emerald-500 bg-emerald-50 dark:bg-emerald-900/20" },
  message_received:{ icon: Inbox,       color: "text-sky-500 bg-sky-50 dark:bg-sky-900/20" },
};

function FeedItem({ event }: { event: FeedEvent }) {
  const meta = FEED_META[event.type];
  const Icon = meta.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -8, height: 0 }}
      animate={{ opacity: 1, x: 0, height: "auto" }}
      exit={{ opacity: 0, x: 8, height: 0 }}
      transition={{ duration: 0.2 }}
      className="flex items-start gap-3 py-2.5 border-b border-border/50 last:border-0"
    >
      <div className={cn("p-1.5 rounded-lg shrink-0 mt-0.5", meta.color)}>
        <Icon className="h-3.5 w-3.5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium leading-snug truncate">{event.title}</p>
        {event.description && (
          <p className="text-xs text-muted-foreground truncate mt-0.5">{event.description}</p>
        )}
      </div>
      <span className="text-[10px] text-muted-foreground shrink-0 tabular-nums mt-0.5">
        {event.at.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
      </span>
    </motion.div>
  );
}

function ActivityFeed() {
  const events = useActivityFeed();

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="h-4 w-4 text-muted-foreground" />
            Atividade ao vivo
          </CardTitle>
          <LiveBadge />
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto min-h-0 px-4 pb-4">
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2 py-8">
            <Activity className="h-8 w-8 text-muted-foreground/30" />
            <p className="text-xs text-muted-foreground text-center">
              Aguardando eventos…
              <br />
              <span className="text-[11px]">Crie um lead, mova no pipeline ou envie uma mensagem</span>
            </p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {events.map((e) => (
              <FeedItem key={e.id} event={e} />
            ))}
          </AnimatePresence>
        )}
      </CardContent>
    </Card>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { data: board = [], isLoading: boardLoading } = useBoard();
  const { data: taskSummary } = useTaskSummary();
  const { data: leads = [] } = useLeads();

  const totalLeads = leads.length;
  const totalValue = leads.reduce((acc, l) => acc + (l.value ?? 0), 0);


  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Visão geral do seu pipeline comercial</p>
        </div>
        <LiveBadge />
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricsCard
          title="Total de Leads"
          value={totalLeads}
          description="No pipeline atual"
          icon={Users}
        />
        <MetricsCard
          title="Valor do Pipeline"
          value={totalValue.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
          description="Soma de todos os leads"
          icon={TrendingUp}
          variant="success"
        />
        <MetricsCard
          title="Tarefas Hoje"
          value={taskSummary?.due_today ?? 0}
          description={`${taskSummary?.overdue ?? 0} atrasada${taskSummary?.overdue !== 1 ? "s" : ""}`}
          icon={CheckSquare}
          variant={taskSummary?.overdue ? "warning" : "default"}
        />
        <MetricsCard
          title="Tarefas Vencidas"
          value={taskSummary?.overdue ?? 0}
          description="Precisam de atenção"
          icon={AlertCircle}
          variant={taskSummary?.overdue ? "danger" : "default"}
        />
      </div>

      {/* Kanban + Feed */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6">
        {/* Kanban */}
        <div className="space-y-3 min-w-0">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Pipeline de Vendas</h2>
            <p className="text-sm text-muted-foreground">
              {board.reduce((acc, col) => acc + col.leads.length, 0)} leads ativos
            </p>
          </div>

          {boardLoading ? (
            <div className="flex gap-4 overflow-x-auto pb-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="min-w-[280px] h-64 bg-muted/50 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : board.length > 0 ? (
            <KanbanBoard columns={board} />
          ) : (
            <div className="flex flex-col items-center justify-center h-48 bg-muted/30 rounded-lg border-2 border-dashed border-border">
              <MessageSquare className="h-10 w-10 text-muted-foreground mb-3" />
              <p className="text-muted-foreground font-medium">Nenhum estágio configurado</p>
              <p className="text-sm text-muted-foreground">Configure seu pipeline em Configurações</p>
            </div>
          )}
        </div>

        {/* Activity feed */}
        <div className="h-[420px] xl:h-auto">
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
