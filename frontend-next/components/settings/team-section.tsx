"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  UserPlus,
  Shield,
  Trash2,
  Check,
  X,
  ChevronDown,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { settingsService } from "@/services/settings.service";
import { useAuthStore } from "@/store/auth.store";
import type { WorkspaceMember, InviteUser } from "@/types";
import { cn } from "@/lib/utils";

const ROLE_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  admin:   { label: "Admin",   variant: "default" },
  manager: { label: "Gerente", variant: "secondary" },
  sales:   { label: "Vendas",  variant: "outline" },
};

function initials(name: string) {
  return name.split(" ").slice(0, 2).map((w) => w[0]).join("").toUpperCase();
}

// ── Invite Dialog ─────────────────────────────────────────────────────────────

function InviteDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<InviteUser>({ name: "", email: "", password: "", role: "sales" });

  const mutation = useMutation({
    mutationFn: settingsService.inviteMember,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      setForm({ name: "", email: "", password: "", role: "sales" });
      onClose();
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || form.password.length < 6) return;
    mutation.mutate(form);
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Convidar membro</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          <div className="space-y-2">
            <Label htmlFor="inv-name">Nome completo *</Label>
            <Input
              id="inv-name"
              autoFocus
              placeholder="João Silva"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="inv-email">E-mail *</Label>
            <Input
              id="inv-email"
              type="email"
              placeholder="joao@empresa.com"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="inv-password">Senha inicial *</Label>
            <Input
              id="inv-password"
              type="password"
              placeholder="Mínimo 6 caracteres"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              required
              minLength={6}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="inv-role">Função</Label>
            <select
              id="inv-role"
              value={form.role}
              onChange={(e) => setForm((f) => ({ ...f, role: e.target.value as InviteUser["role"] }))}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="sales">Vendas — acessa seus próprios leads</option>
              <option value="manager">Gerente — gerencia leads e pipeline</option>
              <option value="admin">Admin — acesso total ao workspace</option>
            </select>
          </div>

          {mutation.isError && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              {(mutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Erro ao convidar membro"}
            </p>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
            <Button type="submit" disabled={mutation.isPending || form.password.length < 6}>
              {mutation.isPending ? "Convidando..." : "Convidar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ── Member Row ────────────────────────────────────────────────────────────────

function MemberRow({ member, isSelf }: { member: WorkspaceMember; isSelf: boolean }) {
  const queryClient = useQueryClient();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const roleInfo = ROLE_CONFIG[member.role] ?? { label: member.role, variant: "outline" as const };

  const updateMutation = useMutation({
    mutationFn: (payload: { role?: string; is_active?: boolean }) =>
      settingsService.updateMember(member.id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["team-members"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: () => settingsService.removeMember(member.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      setConfirmDelete(false);
    },
  });

  return (
    <div className={cn(
      "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors hover:bg-muted/40",
      !member.is_active && "opacity-55"
    )}>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="text-xs font-bold bg-primary/10 text-primary">
          {initials(member.name)}
        </AvatarFallback>
      </Avatar>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium truncate">{member.name}</p>
          {isSelf && <span className="text-[10px] text-muted-foreground">(você)</span>}
          {!member.is_active && (
            <Badge variant="outline" className="text-[10px] px-1">Inativo</Badge>
          )}
        </div>
        <p className="text-xs text-muted-foreground truncate">{member.email}</p>
      </div>

      <Badge variant={roleInfo.variant} className="shrink-0 text-xs">{roleInfo.label}</Badge>

      {!isSelf && (
        <div className="flex items-center gap-1 shrink-0">
          {confirmDelete ? (
            <>
              <Button
                variant="destructive"
                size="icon"
                className="h-7 w-7"
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
                title="Confirmar remoção"
              >
                <Check className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={() => setConfirmDelete(false)}
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            </>
          ) : (
            <>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs px-2">
                    <Shield className="h-3 w-3" />
                    Função
                    <ChevronDown className="h-3 w-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  {Object.entries(ROLE_CONFIG).map(([role, { label }]) => (
                    <DropdownMenuItem
                      key={role}
                      className={cn("text-xs gap-2", member.role === role && "font-semibold")}
                      onClick={() => updateMutation.mutate({ role })}
                    >
                      {member.role === role && <Check className="h-3 w-3" />}
                      {label}
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-xs"
                    onClick={() => updateMutation.mutate({ is_active: !member.is_active })}
                  >
                    {member.is_active ? "Desativar acesso" : "Reativar acesso"}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-muted-foreground hover:text-destructive"
                onClick={() => setConfirmDelete(true)}
                title="Remover membro"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ── TeamSection ───────────────────────────────────────────────────────────────

export function TeamSection() {
  const { user } = useAuthStore();
  const [inviteOpen, setInviteOpen] = useState(false);

  const { data: members = [], isLoading } = useQuery<WorkspaceMember[]>({
    queryKey: ["team-members"],
    queryFn: settingsService.getMembers,
  });

  return (
    <div className="space-y-5">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Membros do workspace</CardTitle>
              <CardDescription>Gerencie a equipe e suas permissões de acesso</CardDescription>
            </div>
            <Button size="sm" onClick={() => setInviteOpen(true)}>
              <UserPlus className="h-4 w-4" />
              Convidar
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-12 bg-muted/50 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : members.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              Nenhum membro encontrado
            </p>
          ) : (
            <div className="space-y-0.5">
              {members.map((member) => (
                <MemberRow
                  key={member.id}
                  member={member}
                  isSelf={member.id === user?.id}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-dashed bg-muted/20">
        <CardContent className="pt-4 pb-3">
          <p className="text-xs text-muted-foreground">
            <strong>Funções:</strong> Admin tem acesso total ao workspace · Gerente gerencia leads, pipeline e inbox · Vendas acessa apenas seus próprios leads e tarefas.
          </p>
        </CardContent>
      </Card>

      <InviteDialog open={inviteOpen} onClose={() => setInviteOpen(false)} />
    </div>
  );
}
