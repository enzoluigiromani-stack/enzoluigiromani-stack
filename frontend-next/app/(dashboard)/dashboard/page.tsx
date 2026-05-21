"use client";

import { useQuery } from "@tanstack/react-query";
import { Users, MessageSquare, CheckSquare, AlertCircle, TrendingUp } from "lucide-react";
import { MetricsCard } from "@/components/dashboard/metrics-card";
import { KanbanBoard } from "@/components/dashboard/kanban-board";
import { leadsService } from "@/services/leads.service";
import { api } from "@/services/api";
import type { TaskSummary, KanbanColumn } from "@/types";

function useBoard() {
  return useQuery<KanbanColumn[]>({
    queryKey: ["board"],
    queryFn: leadsService.getBoard,
  });
}

function useTaskSummary() {
  return useQuery<TaskSummary>({
    queryKey: ["task-summary"],
    queryFn: async () => {
      const { data } = await api.get<TaskSummary>("/tasks/summary");
      return data;
    },
  });
}

function useLeads() {
  return useQuery({
    queryKey: ["leads"],
    queryFn: leadsService.getLeads,
  });
}

export default function DashboardPage() {
  const { data: board = [], isLoading: boardLoading } = useBoard();
  const { data: taskSummary } = useTaskSummary();
  const { data: leads = [] } = useLeads();

  const totalLeads = leads.length;
  const totalValue = leads.reduce((acc, l) => acc + (l.value ?? 0), 0);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral do seu pipeline comercial</p>
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
          description={`${taskSummary?.overdue ?? 0} atrasadas`}
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

      {/* Kanban */}
      <div className="space-y-4">
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
    </div>
  );
}
