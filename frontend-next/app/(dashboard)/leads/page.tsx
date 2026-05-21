"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Plus, Search, User, DollarSign, Filter, RefreshCw, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { leadsService } from "@/services/leads.service";
import { realtimeClient } from "@/services/websocket.service";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import type { Lead, LeadCreate, Stage } from "@/types";
import { api } from "@/services/api";
import { cn } from "@/lib/utils";

const STATUS_BADGE: Record<string, { label: string; variant: "default" | "secondary" | "outline" | "destructive" }> = {
  active: { label: "Ativo", variant: "default" },
  won: { label: "Ganho", variant: "secondary" },
  lost: { label: "Perdido", variant: "destructive" },
  inactive: { label: "Inativo", variant: "outline" },
};

const HIGHLIGHT_TTL = 4000;

// ── Flash hook ────────────────────────────────────────────────────────────────

function useLeadFlash() {
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
      if (event.channel !== "pipeline_updates") return;
      if (event.event === "lead.created") flash((event.payload as Lead).id);
      if (event.event === "lead.updated") flash((event.payload as Lead).id);
      if (event.event === "lead.moved") flash((event.payload as { lead_id: number }).lead_id);
    });
    return off;
  }, [flash]);

  return flashIds;
}

// ── Live badge ─────────────────────────────────────────────────────────────────

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

function CreateLeadDialog({ stages }: { stages: Stage[] }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<LeadCreate>({ name: "" });

  const mutation = useMutation({
    mutationFn: leadsService.createLead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      setOpen(false);
      setForm({ name: "" });
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate(form);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4" />
          Novo Lead
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Novo Lead</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          <div className="space-y-2">
            <Label htmlFor="name">Nome *</Label>
            <Input
              id="name"
              placeholder="Nome do lead"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="email@exemplo.com"
                value={form.email ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value || undefined }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Telefone</Label>
              <Input
                id="phone"
                placeholder="+55 11 99999-9999"
                value={form.phone ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value || undefined }))}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="company">Empresa</Label>
              <Input
                id="company"
                placeholder="Nome da empresa"
                value={form.company ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, company: e.target.value || undefined }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="value">Valor (R$)</Label>
              <Input
                id="value"
                type="number"
                placeholder="0,00"
                value={form.value ?? ""}
                onChange={(e) =>
                  setForm((f) => ({ ...f, value: e.target.value ? Number(e.target.value) : undefined }))
                }
              />
            </div>
          </div>

          {stages.length > 0 && (
            <div className="space-y-2">
              <Label htmlFor="stage">Estágio</Label>
              <select
                id="stage"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={form.stage_id ?? ""}
                onChange={(e) =>
                  setForm((f) => ({ ...f, stage_id: e.target.value ? Number(e.target.value) : undefined }))
                }
              >
                <option value="">Sem estágio</option>
                {stages.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Criando..." : "Criar Lead"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function LeadsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const flashIds = useLeadFlash();

  const { data: leads = [], isLoading } = useQuery<Lead[]>({
    queryKey: ["leads"],
    queryFn: leadsService.getLeads,
    staleTime: 30_000,
  });

  const { data: board = [] } = useQuery({
    queryKey: ["board"],
    queryFn: leadsService.getBoard,
  });

  const stages = board.map((col) => col.stage);

  const { data: stagesData = [] } = useQuery<Stage[]>({
    queryKey: ["stages"],
    queryFn: async () => {
      const { data } = await api.get<Stage[]>("/pipeline/stages");
      return data;
    },
  });

  const allStages = stagesData.length > 0 ? stagesData : stages;

  const filtered = leads.filter((l) => {
    const matchSearch =
      !search ||
      l.name.toLowerCase().includes(search.toLowerCase()) ||
      l.email?.toLowerCase().includes(search.toLowerCase()) ||
      l.company?.toLowerCase().includes(search.toLowerCase());
    const matchStatus = !statusFilter || l.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Leads</h1>
          <p className="text-muted-foreground">
            {leads.length} leads no total
          </p>
        </div>
        <div className="flex items-center gap-3">
          <LiveBadge />
          <CreateLeadDialog stages={allStages} />
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome, email ou empresa..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Todos os status</option>
            <option value="active">Ativo</option>
            <option value="won">Ganho</option>
            <option value="lost">Perdido</option>
            <option value="inactive">Inativo</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="border rounded-lg bg-card">
        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <div className="text-muted-foreground">Carregando leads...</div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 gap-2">
            <User className="h-10 w-10 text-muted-foreground" />
            <p className="text-muted-foreground font-medium">
              {search || statusFilter ? "Nenhum lead encontrado" : "Nenhum lead cadastrado"}
            </p>
            {!search && !statusFilter && (
              <p className="text-sm text-muted-foreground">Clique em &quot;Novo Lead&quot; para começar</p>
            )}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Empresa</TableHead>
                <TableHead>Contato</TableHead>
                <TableHead>Estágio</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Criado em</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((lead) => {
                const statusInfo = STATUS_BADGE[lead.status] ?? { label: lead.status, variant: "outline" as const };
                const isFlashing = flashIds.has(lead.id);
                return (
                  <TableRow
                    key={lead.id}
                    className={cn(
                      "cursor-pointer transition-colors duration-700",
                      isFlashing && "bg-primary/5",
                    )}
                    onClick={() => router.push(`/leads/${lead.id}`)}
                  >
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {isFlashing && (
                          <span className="relative flex h-1.5 w-1.5 shrink-0">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-60" />
                            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-primary" />
                          </span>
                        )}
                        <div>
                          <div className="font-medium">{lead.name}</div>
                          {lead.tags && lead.tags.length > 0 && (
                            <div className="flex gap-1 mt-1">
                              {lead.tags.slice(0, 2).map((tag) => (
                                <span
                                  key={tag}
                                  className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-secondary-foreground font-medium"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {lead.company ?? "—"}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{lead.email ?? "—"}</div>
                      <div className="text-xs text-muted-foreground">{lead.phone}</div>
                    </TableCell>
                    <TableCell>
                      {lead.stage ? (
                        <div className="flex items-center gap-1.5">
                          <div
                            className="h-2 w-2 rounded-full shrink-0"
                            style={{ backgroundColor: lead.stage.color ?? "#6366f1" }}
                          />
                          <span className="text-sm">{lead.stage.name}</span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-sm">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {lead.value ? (
                        <div className="flex items-center gap-1 text-green-600 font-medium text-sm">
                          <DollarSign className="h-3 w-3" />
                          {lead.value.toLocaleString("pt-BR", {
                            style: "currency",
                            currency: "BRL",
                          })}
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-sm">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {new Date(lead.created_at).toLocaleDateString("pt-BR")}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
