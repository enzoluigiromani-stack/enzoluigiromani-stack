"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Phone,
  Mail,
  Building2,
  DollarSign,
  Clock,
  Tag,
  MessageSquare,
  CheckSquare,
  RefreshCw,
  WifiOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { leadsService } from "@/services/leads.service";
import { tasksService } from "@/services/tasks.service";
import { realtimeClient } from "@/services/websocket.service";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import { api } from "@/services/api";
import type { Lead, Activity, Task } from "@/types";
import { cn } from "@/lib/utils";

// ── Config ────────────────────────────────────────────────────────────────────

const ACTIVITY_ICONS: Record<string, string> = {
  note: "📝",
  call: "📞",
  email: "📧",
  meeting: "🤝",
  stage_change: "📊",
  task_created: "✅",
  lead_created: "🎉",
  capture: "📥",
  default: "💬",
};

const PRIORITY_COLORS: Record<string, string> = {
  high: "text-destructive",
  medium: "text-yellow-600",
  low: "text-muted-foreground",
};

const TASK_STATUS: Record<string, { label: string; variant: "default" | "secondary" | "outline" | "destructive" }> = {
  pending: { label: "Pendente", variant: "outline" },
  overdue: { label: "Atrasada", variant: "destructive" },
  completed: { label: "Concluída", variant: "secondary" },
};

// ── Sub-components ────────────────────────────────────────────────────────────

function ActivityItem({ activity }: { activity: Activity }) {
  const icon = ACTIVITY_ICONS[activity.type] ?? ACTIVITY_ICONS.default;
  return (
    <div className="flex gap-3 py-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center text-sm">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm leading-relaxed">{activity.description}</p>
        <p className="text-xs text-muted-foreground mt-0.5">
          {new Date(activity.created_at).toLocaleString("pt-BR")}
        </p>
      </div>
    </div>
  );
}

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

// ── Page ──────────────────────────────────────────────────────────────────────

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const leadId = Number(id);
  const router = useRouter();
  const queryClient = useQueryClient();
  const [noteText, setNoteText] = useState("");

  const { data: lead, isLoading } = useQuery<Lead>({
    queryKey: ["lead", id],
    queryFn: async () => {
      const { data } = await api.get<Lead>(`/leads/${id}`);
      return data;
    },
    enabled: !!id,
  });

  const { data: timelineData } = useQuery({
    queryKey: ["lead-timeline", id],
    queryFn: () => leadsService.getTimeline(leadId),
    enabled: !!id,
  });

  const { data: tasks = [] } = useQuery<Task[]>({
    queryKey: ["lead-tasks", id],
    queryFn: () => tasksService.getTasks(undefined, leadId),
    enabled: !!id,
  });

  // Live updates for this specific lead
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel !== "pipeline_updates") return;

      if (event.event === "lead.updated") {
        const updated = event.payload as Lead;
        if (updated.id !== leadId) return;
        queryClient.setQueryData<Lead>(["lead", id], (old) =>
          old ? { ...old, ...updated } : updated,
        );
      }

      if (event.event === "lead.moved") {
        const { lead_id, lead } = event.payload as { lead_id: number; lead: Lead };
        if (lead_id !== leadId) return;
        queryClient.setQueryData<Lead>(["lead", id], (old) =>
          old ? { ...old, stage_id: lead.stage_id, stage: lead.stage } : old,
        );
        queryClient.invalidateQueries({ queryKey: ["lead-timeline", id] });
      }
    });
    return off;
  }, [id, leadId, queryClient]);

  const noteMutation = useMutation({
    mutationFn: async (description: string) => {
      await api.post("/activities/", {
        lead_id: leadId,
        type: "note",
        description,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lead-timeline", id] });
      setNoteText("");
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Carregando...</div>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-muted-foreground">Lead não encontrado</p>
        <Button variant="outline" onClick={() => router.push("/leads")}>
          <ArrowLeft className="h-4 w-4" />
          Voltar
        </Button>
      </div>
    );
  }

  const activities = (timelineData?.items as Activity[]) ?? [];

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      {/* Back + Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/leads")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold tracking-tight">{lead.name}</h1>
            {lead.status && (
              <Badge variant={lead.status === "active" ? "default" : "secondary"}>
                {lead.status === "active" ? "Ativo" : lead.status}
              </Badge>
            )}
            <LiveBadge />
          </div>
          {lead.stage && (
            <div className="flex items-center gap-1.5 mt-1">
              <div
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: lead.stage.color ?? "#6366f1" }}
              />
              <span className="text-sm text-muted-foreground">{lead.stage.name}</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Info + Tasks */}
        <div className="space-y-4">
          {/* Contact Info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Informações
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {lead.email && (
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span className="truncate">{lead.email}</span>
                </div>
              )}
              {lead.phone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span>{lead.phone}</span>
                </div>
              )}
              {lead.company && (
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span>{lead.company}</span>
                </div>
              )}
              {lead.value && (
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span className="font-medium text-green-600">
                    {lead.value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                  </span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
                <span className="text-muted-foreground">
                  {new Date(lead.created_at).toLocaleDateString("pt-BR")}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* UTM/Source */}
          {(lead.utm_source || lead.campaign_name) && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  Origem
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {lead.utm_source && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Fonte</span>
                    <span className="font-medium">{lead.utm_source}</span>
                  </div>
                )}
                {lead.utm_campaign && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Campanha</span>
                    <span className="font-medium truncate max-w-[140px]">{lead.utm_campaign}</span>
                  </div>
                )}
                {lead.campaign_name && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Nome</span>
                    <span className="font-medium truncate max-w-[140px]">{lead.campaign_name}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Tags */}
          {lead.tags && lead.tags.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                  <Tag className="h-3.5 w-3.5" />
                  Tags
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1.5">
                  {lead.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tasks */}
          {tasks.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                  <CheckSquare className="h-3.5 w-3.5" />
                  Tarefas ({tasks.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {tasks.map((task) => {
                  const status = TASK_STATUS[task.status] ?? { label: task.status, variant: "outline" as const };
                  return (
                    <div key={task.id} className="flex items-start gap-2 text-sm">
                      <div className={`mt-0.5 font-medium ${PRIORITY_COLORS[task.priority]}`}>•</div>
                      <div className="flex-1 min-w-0">
                        <p className="leading-tight truncate">{task.title}</p>
                        {task.due_date && (
                          <p className="text-xs text-muted-foreground">
                            {new Date(task.due_date).toLocaleDateString("pt-BR")}
                          </p>
                        )}
                      </div>
                      <Badge variant={status.variant} className="text-[10px] shrink-0">
                        {status.label}
                      </Badge>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right: Timeline */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                <MessageSquare className="h-3.5 w-3.5" />
                Linha do Tempo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {/* Add note */}
              <div className="space-y-2 pb-4">
                <Textarea
                  placeholder="Adicionar uma nota..."
                  className="min-h-[80px] resize-none"
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                />
                <div className="flex justify-end">
                  <Button
                    size="sm"
                    disabled={!noteText.trim() || noteMutation.isPending}
                    onClick={() => noteMutation.mutate(noteText.trim())}
                  >
                    {noteMutation.isPending ? "Salvando..." : "Salvar nota"}
                  </Button>
                </div>
              </div>

              <Separator />

              {/* Activities */}
              {activities.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 gap-2">
                  <Clock className="h-8 w-8 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Nenhuma atividade registrada</p>
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {activities.map((activity) => (
                    <ActivityItem key={activity.id} activity={activity} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
