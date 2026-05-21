"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Plus, CheckCircle2, Clock, AlertCircle, Circle, RefreshCw, WifiOff,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter,
} from "@/components/ui/dialog";
import { tasksService, type TaskCreate } from "@/services/tasks.service";
import { realtimeClient } from "@/services/websocket.service";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import type { Task } from "@/types";
import { cn } from "@/lib/utils";

// ── Config ────────────────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  pending: {
    label: "Pendente",
    icon: Circle,
    badge: "outline" as const,
    color: "text-muted-foreground",
  },
  overdue: {
    label: "Atrasada",
    icon: AlertCircle,
    badge: "destructive" as const,
    color: "text-destructive",
  },
  completed: {
    label: "Concluída",
    icon: CheckCircle2,
    badge: "secondary" as const,
    color: "text-emerald-600",
  },
} as const;

const PRIORITY_CONFIG = {
  high:   { label: "Alta",  color: "text-destructive",      dot: "bg-destructive" },
  medium: { label: "Média", color: "text-yellow-600",       dot: "bg-yellow-500" },
  low:    { label: "Baixa", color: "text-muted-foreground", dot: "bg-muted-foreground" },
};

const STATUS_FILTERS = [
  { value: "",          label: "Todas" },
  { value: "pending",   label: "Pendentes" },
  { value: "overdue",   label: "Atrasadas" },
  { value: "completed", label: "Concluídas" },
];

// ── Hooks ─────────────────────────────────────────────────────────────────────

const HIGHLIGHT_TTL = 4000;

function useTaskFlash() {
  const [flashIds, setFlashIds] = useState<Set<number>>(new Set());
  const timers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const flash = useCallback((id: number) => {
    setFlashIds((prev) => new Set(prev).add(id));
    if (timers.current.has(id)) clearTimeout(timers.current.get(id));
    timers.current.set(
      id,
      setTimeout(() => {
        setFlashIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
        timers.current.delete(id);
      }, HIGHLIGHT_TTL),
    );
  }, []);

  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel !== "task_updates") return;
      if (event.event === "task.created" || event.event === "task.updated") {
        flash((event.payload as { id: number }).id);
      }
    });
    return off;
  }, [flash]);

  return flashIds;
}

// ── Live badge ────────────────────────────────────────────────────────────────

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

// ── Create dialog ─────────────────────────────────────────────────────────────

function CreateTaskDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<TaskCreate>({ title: "", priority: "medium" });

  const mutation = useMutation({
    mutationFn: tasksService.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["task-summary"] });
      setOpen(false);
      setForm({ title: "", priority: "medium" });
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button><Plus className="h-4 w-4" /> Nova Tarefa</Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Nova Tarefa</DialogTitle>
        </DialogHeader>

        <form
          onSubmit={(e) => { e.preventDefault(); mutation.mutate(form); }}
          className="space-y-4 py-2"
        >
          <div className="space-y-2">
            <Label htmlFor="title">Título *</Label>
            <Input
              id="title"
              placeholder="Descreva a tarefa..."
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descrição</Label>
            <Textarea
              id="description"
              placeholder="Detalhes opcionais..."
              className="resize-none min-h-[80px]"
              value={form.description ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value || undefined }))}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="priority">Prioridade</Label>
              <select
                id="priority"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value as TaskCreate["priority"] }))}
              >
                <option value="low">Baixa</option>
                <option value="medium">Média</option>
                <option value="high">Alta</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="due_date">Prazo</Label>
              <Input
                id="due_date"
                type="date"
                value={form.due_date ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value || undefined }))}
              />
            </div>
          </div>

          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Criando..." : "Criar Tarefa"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ── Task card ─────────────────────────────────────────────────────────────────

function TaskCard({ task, isFlashing }: { task: Task; isFlashing: boolean }) {
  const queryClient = useQueryClient();
  const statusInfo = STATUS_CONFIG[task.status] ?? STATUS_CONFIG.pending;
  const priorityInfo = PRIORITY_CONFIG[task.priority] ?? PRIORITY_CONFIG.medium;
  const StatusIcon = statusInfo.icon;
  const isDone = task.status === "completed";

  const completeMutation = useMutation({
    mutationFn: () => tasksService.completeTask(task.id),

    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      // Optimistic: mark as completed in all task caches
      queryClient
        .getQueriesData<Task[]>({ queryKey: ["tasks"] })
        .forEach(([key, data]) => {
          if (!data) return;
          queryClient.setQueryData<Task[]>(
            key,
            data.map((t) => t.id === task.id ? { ...t, status: "completed" } : t),
          );
        });
    },

    onError: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["task-summary"] });
    },
  });

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4, scale: 0.97 }}
      transition={{ duration: 0.15 }}
    >
      <Card className={cn(
        "transition-all duration-500",
        isDone && "opacity-55",
        isFlashing && "ring-2 ring-primary/40 shadow-[0_0_12px_2px] shadow-primary/15",
      )}>
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <button
              onClick={() => { if (!isDone) completeMutation.mutate(); }}
              disabled={isDone || completeMutation.isPending}
              className={cn(
                "mt-0.5 shrink-0 transition-colors",
                isDone ? "text-emerald-600" : "text-muted-foreground hover:text-primary",
              )}
              title={isDone ? "Concluída" : "Marcar como concluída"}
            >
              <StatusIcon className={cn("h-5 w-5", completeMutation.isPending && "animate-spin")} />
            </button>

            <div className="flex-1 min-w-0">
              <p className={cn(
                "text-sm font-medium leading-tight",
                isDone && "line-through text-muted-foreground",
              )}>
                {task.title}
              </p>

              {task.description && (
                <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                  {task.description}
                </p>
              )}

              {(task.lead_name || task.assigned_user_name) && (
                <p className="text-xs text-muted-foreground mt-1 truncate">
                  {[task.lead_name && `Lead: ${task.lead_name}`, task.assigned_user_name && `→ ${task.assigned_user_name}`]
                    .filter(Boolean).join(" · ")}
                </p>
              )}

              <div className="flex items-center gap-3 mt-2 flex-wrap">
                <div className="flex items-center gap-1">
                  <div className={cn("h-1.5 w-1.5 rounded-full", priorityInfo.dot)} />
                  <span className={cn("text-xs", priorityInfo.color)}>{priorityInfo.label}</span>
                </div>

                {task.due_date && (
                  <span className={cn(
                    "text-xs",
                    task.status === "overdue" ? "text-destructive font-medium" : "text-muted-foreground",
                  )}>
                    {task.status === "overdue" ? "Atrasada · " : ""}
                    {new Date(task.due_date).toLocaleDateString("pt-BR")}
                  </span>
                )}
              </div>
            </div>

            <Badge variant={statusInfo.badge} className="shrink-0 text-xs">
              {statusInfo.label}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function TasksPage() {
  const [statusFilter, setStatusFilter] = useState("");
  const flashIds = useTaskFlash();

  const { data: tasks = [], isLoading } = useQuery<Task[]>({
    queryKey: ["tasks", statusFilter],
    queryFn: () => tasksService.getTasks(statusFilter || undefined),
    staleTime: 30_000,
  });

  const overdue = tasks.filter((t) => t.status === "overdue").length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tarefas</h1>
          <p className="text-muted-foreground">
            {tasks.length} tarefa{tasks.length !== 1 ? "s" : ""}
            {overdue > 0 && (
              <span className="text-destructive ml-1">
                · {overdue} atrasada{overdue !== 1 ? "s" : ""}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <LiveBadge />
          <CreateTaskDialog />
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-lg w-fit">
        {STATUS_FILTERS.map(({ value, label }) => {
          const count = value === "overdue" ? overdue : undefined;
          return (
            <button
              key={value}
              onClick={() => setStatusFilter(value)}
              className={cn(
                "relative px-3 py-1.5 text-sm rounded-md font-medium transition-colors",
                statusFilter === value
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {label}
              {count != null && count > 0 && (
                <span className="ml-1.5 inline-flex items-center justify-center h-4 min-w-[16px] px-1 rounded-full text-[10px] font-semibold bg-destructive text-destructive-foreground">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-muted/50 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : tasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-48 gap-2">
          <CheckCircle2 className="h-10 w-10 text-muted-foreground" />
          <p className="text-muted-foreground font-medium">
            {statusFilter ? "Nenhuma tarefa com esse status" : "Nenhuma tarefa cadastrada"}
          </p>
          {!statusFilter && (
            <p className="text-sm text-muted-foreground">
              Clique em &quot;Nova Tarefa&quot; para começar
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <AnimatePresence mode="popLayout">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                isFlashing={flashIds.has(task.id)}
              />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
