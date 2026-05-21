"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, CheckCircle2, Clock, AlertCircle, Circle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { tasksService, type TaskCreate } from "@/services/tasks.service";
import type { Task } from "@/types";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  pending: {
    label: "Pendente",
    icon: Circle,
    badge: "outline" as const,
    color: "text-muted-foreground",
  },
  in_progress: {
    label: "Em andamento",
    icon: Clock,
    badge: "default" as const,
    color: "text-blue-600",
  },
  completed: {
    label: "Concluída",
    icon: CheckCircle2,
    badge: "secondary" as const,
    color: "text-green-600",
  },
  cancelled: {
    label: "Cancelada",
    icon: AlertCircle,
    badge: "destructive" as const,
    color: "text-muted-foreground",
  },
};

const PRIORITY_CONFIG = {
  high: { label: "Alta", color: "text-destructive", dot: "bg-destructive" },
  medium: { label: "Média", color: "text-yellow-600", dot: "bg-yellow-500" },
  low: { label: "Baixa", color: "text-muted-foreground", dot: "bg-muted-foreground" },
};

function CreateTaskDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<TaskCreate>({
    title: "",
    priority: "medium",
  });

  const mutation = useMutation({
    mutationFn: tasksService.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setOpen(false);
      setForm({ title: "", priority: "medium" });
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4" />
          Nova Tarefa
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Nova Tarefa</DialogTitle>
        </DialogHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate(form);
          }}
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
              onChange={(e) =>
                setForm((f) => ({ ...f, description: e.target.value || undefined }))
              }
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="priority">Prioridade</Label>
              <select
                id="priority"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={form.priority}
                onChange={(e) =>
                  setForm((f) => ({ ...f, priority: e.target.value as TaskCreate["priority"] }))
                }
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
                onChange={(e) =>
                  setForm((f) => ({ ...f, due_date: e.target.value || undefined }))
                }
              />
            </div>
          </div>

          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Criando..." : "Criar Tarefa"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function TaskCard({ task }: { task: Task }) {
  const queryClient = useQueryClient();
  const statusInfo = STATUS_CONFIG[task.status] ?? STATUS_CONFIG.pending;
  const priorityInfo = PRIORITY_CONFIG[task.priority] ?? PRIORITY_CONFIG.medium;
  const StatusIcon = statusInfo.icon;
  const isOverdue =
    task.due_date &&
    task.status !== "completed" &&
    task.status !== "cancelled" &&
    new Date(task.due_date) < new Date();

  const completeMutation = useMutation({
    mutationFn: () => tasksService.updateTask(task.id, { status: "completed" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks"] }),
  });

  return (
    <Card
      className={cn(
        "transition-all hover:shadow-sm",
        task.status === "completed" && "opacity-60"
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* Complete button */}
          <button
            onClick={() => {
              if (task.status !== "completed") completeMutation.mutate();
            }}
            className={cn(
              "mt-0.5 shrink-0 transition-colors",
              task.status === "completed"
                ? "text-green-600"
                : "text-muted-foreground hover:text-primary"
            )}
            title={task.status === "completed" ? "Concluída" : "Marcar como concluída"}
          >
            <StatusIcon className="h-5 w-5" />
          </button>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <p
              className={cn(
                "text-sm font-medium leading-tight",
                task.status === "completed" && "line-through text-muted-foreground"
              )}
            >
              {task.title}
            </p>

            {task.description && (
              <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                {task.description}
              </p>
            )}

            <div className="flex items-center gap-3 mt-2">
              {/* Priority */}
              <div className="flex items-center gap-1">
                <div className={cn("h-1.5 w-1.5 rounded-full", priorityInfo.dot)} />
                <span className={cn("text-xs", priorityInfo.color)}>{priorityInfo.label}</span>
              </div>

              {/* Due date */}
              {task.due_date && (
                <span
                  className={cn(
                    "text-xs",
                    isOverdue ? "text-destructive font-medium" : "text-muted-foreground"
                  )}
                >
                  {isOverdue ? "Atrasada · " : ""}
                  {new Date(task.due_date).toLocaleDateString("pt-BR")}
                </span>
              )}
            </div>
          </div>

          {/* Status badge */}
          <Badge variant={statusInfo.badge} className="shrink-0 text-xs">
            {statusInfo.label}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

const STATUS_FILTERS = [
  { value: "", label: "Todas" },
  { value: "pending", label: "Pendentes" },
  { value: "in_progress", label: "Em andamento" },
  { value: "completed", label: "Concluídas" },
  { value: "cancelled", label: "Canceladas" },
];

export default function TasksPage() {
  const [statusFilter, setStatusFilter] = useState("");

  const { data: tasks = [], isLoading } = useQuery<Task[]>({
    queryKey: ["tasks", statusFilter],
    queryFn: () => tasksService.getTasks(statusFilter || undefined),
  });

  const overdue = tasks.filter(
    (t) =>
      t.due_date &&
      t.status !== "completed" &&
      t.status !== "cancelled" &&
      new Date(t.due_date) < new Date()
  ).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tarefas</h1>
          <p className="text-muted-foreground">
            {tasks.length} tarefa{tasks.length !== 1 ? "s" : ""}
            {overdue > 0 && (
              <span className="text-destructive ml-1">· {overdue} atrasada{overdue !== 1 ? "s" : ""}</span>
            )}
          </p>
        </div>
        <CreateTaskDialog />
      </div>

      {/* Status filter tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-lg w-fit">
        {STATUS_FILTERS.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setStatusFilter(value)}
            className={cn(
              "px-3 py-1.5 text-sm rounded-md font-medium transition-colors",
              statusFilter === value
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Task list */}
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
            <p className="text-sm text-muted-foreground">Clique em &quot;Nova Tarefa&quot; para começar</p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
}
