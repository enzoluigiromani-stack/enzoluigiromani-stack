"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Plus,
  Pencil,
  Trash2,
  ChevronUp,
  ChevronDown,
  Check,
  X,
  GripVertical,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { settingsService } from "@/services/settings.service";
import { BOARD_QUERY_KEY } from "@/hooks/use-pipeline";
import type { Stage, StageCreate, StageUpdate } from "@/types";
import { cn } from "@/lib/utils";

const PRESET_COLORS = [
  "#6366f1", "#8b5cf6", "#ec4899", "#ef4444",
  "#f97316", "#eab308", "#22c55e", "#06b6d4",
  "#3b82f6", "#64748b", "#14b8a6", "#f43f5e",
];

function ColorPicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (c: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label>Cor do estágio</Label>
      <div className="flex flex-wrap gap-2 items-center">
        {PRESET_COLORS.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => onChange(c)}
            className={cn(
              "h-6 w-6 rounded-full transition-all shrink-0",
              value === c ? "ring-2 ring-offset-2 ring-foreground scale-110" : "hover:scale-105"
            )}
            style={{ backgroundColor: c }}
          />
        ))}
        <div className="flex items-center gap-1.5">
          <input
            type="color"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="h-6 w-6 rounded-full cursor-pointer border border-border p-0 bg-transparent"
          />
          <span className="text-xs text-muted-foreground font-mono">{value}</span>
        </div>
      </div>
    </div>
  );
}

interface StageFormDialogProps {
  open: boolean;
  onClose: () => void;
  stage?: Stage;
  nextOrder: number;
}

function StageFormDialog({ open, onClose, stage, nextOrder }: StageFormDialogProps) {
  const queryClient = useQueryClient();
  const isEdit = !!stage;

  const [form, setForm] = useState<{ name: string; color: string }>({
    name: stage?.name ?? "",
    color: stage?.color ?? PRESET_COLORS[0],
  });

  const createMutation = useMutation({
    mutationFn: (payload: StageCreate) => settingsService.createStage(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stages"] });
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: StageUpdate) => settingsService.updateStage(stage!.id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stages"] });
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY });
      onClose();
    },
  });

  const isPending = createMutation.isPending || updateMutation.isPending;
  const error = createMutation.error || updateMutation.error;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;

    if (isEdit) {
      updateMutation.mutate({ name: form.name.trim(), color: form.color });
    } else {
      createMutation.mutate({ name: form.name.trim(), color: form.color, order: nextOrder });
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Editar estágio" : "Novo estágio"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          <div className="space-y-2">
            <Label htmlFor="stage-name">Nome *</Label>
            <div className="flex items-center gap-2">
              <div
                className="h-8 w-8 rounded-full shrink-0"
                style={{ backgroundColor: form.color }}
              />
              <Input
                id="stage-name"
                autoFocus
                placeholder="Ex: Proposta enviada"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                required
              />
            </div>
          </div>

          <ColorPicker
            value={form.color}
            onChange={(c) => setForm((f) => ({ ...f, color: c }))}
          />

          {error && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              {(error as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? "Erro ao salvar"}
            </p>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending || !form.name.trim()}>
              {isPending ? "Salvando..." : isEdit ? "Salvar" : "Criar estágio"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

interface StageRowProps {
  stage: Stage;
  index: number;
  total: number;
  onEdit: () => void;
  onDelete: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}

function StageRow({ stage, index, total, onEdit, onDelete, onMoveUp, onMoveDown }: StageRowProps) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div className="group flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted/50 transition-colors border border-transparent hover:border-border">
      <GripVertical className="h-4 w-4 text-muted-foreground/30 shrink-0" />

      <div
        className="h-3 w-3 rounded-full shrink-0"
        style={{ backgroundColor: stage.color ?? "#6366f1" }}
      />

      <span className="flex-1 text-sm font-medium">{stage.name}</span>

      <Badge variant="outline" className="text-[10px] font-mono shrink-0">
        #{stage.order}
      </Badge>

      {/* Order buttons */}
      <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={onMoveUp}
          disabled={index === 0}
          title="Mover para cima"
        >
          <ChevronUp className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={onMoveDown}
          disabled={index === total - 1}
          title="Mover para baixo"
        >
          <ChevronDown className="h-3 w-3" />
        </Button>
      </div>

      {/* Action buttons */}
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={onEdit}
          title="Editar"
        >
          <Pencil className="h-3.5 w-3.5" />
        </Button>

        {confirmDelete ? (
          <div className="flex items-center gap-1">
            <Button
              variant="destructive"
              size="icon"
              className="h-7 w-7"
              onClick={onDelete}
              title="Confirmar exclusão"
            >
              <Check className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setConfirmDelete(false)}
              title="Cancelar"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-muted-foreground hover:text-destructive"
            onClick={() => setConfirmDelete(true)}
            title="Excluir estágio"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>
    </div>
  );
}

export function PipelineSection() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editStage, setEditStage] = useState<Stage | undefined>();

  const { data: stages = [], isLoading } = useQuery<Stage[]>({
    queryKey: ["stages"],
    queryFn: settingsService.getStages,
  });

  const deleteMutation = useMutation({
    mutationFn: settingsService.deleteStage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stages"] });
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY });
    },
  });

  const reorderMutation = useMutation({
    mutationFn: ({ id, order }: { id: number; order: number }) =>
      settingsService.updateStage(id, { order }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stages"] });
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY });
    },
  });

  function handleMoveUp(index: number) {
    if (index === 0) return;
    const a = stages[index];
    const b = stages[index - 1];
    reorderMutation.mutate({ id: a.id, order: b.order });
    reorderMutation.mutate({ id: b.id, order: a.order });
  }

  function handleMoveDown(index: number) {
    if (index === stages.length - 1) return;
    const a = stages[index];
    const b = stages[index + 1];
    reorderMutation.mutate({ id: a.id, order: b.order });
    reorderMutation.mutate({ id: b.id, order: a.order });
  }

  function openCreate() {
    setEditStage(undefined);
    setDialogOpen(true);
  }

  function openEdit(stage: Stage) {
    setEditStage(stage);
    setDialogOpen(true);
  }

  const nextOrder = stages.length > 0 ? Math.max(...stages.map((s) => s.order)) + 1 : 1;

  return (
    <div className="space-y-5">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Estágios do Pipeline</CardTitle>
              <CardDescription>
                Configure as etapas do seu funil de vendas
              </CardDescription>
            </div>
            <Button size="sm" onClick={openCreate}>
              <Plus className="h-4 w-4" />
              Novo estágio
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-10 bg-muted/50 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : stages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 gap-2">
              <p className="text-sm text-muted-foreground">Nenhum estágio cadastrado</p>
              <Button variant="outline" size="sm" onClick={openCreate}>
                <Plus className="h-4 w-4" />
                Criar primeiro estágio
              </Button>
            </div>
          ) : (
            <div className="space-y-0.5">
              {stages.map((stage, i) => (
                <StageRow
                  key={stage.id}
                  stage={stage}
                  index={i}
                  total={stages.length}
                  onEdit={() => openEdit(stage)}
                  onDelete={() => deleteMutation.mutate(stage.id)}
                  onMoveUp={() => handleMoveUp(i)}
                  onMoveDown={() => handleMoveDown(i)}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-dashed bg-muted/20">
        <CardContent className="pt-4 pb-3">
          <p className="text-xs text-muted-foreground">
            <strong>Dica:</strong> Ao excluir um estágio, os leads vinculados a ele são movidos para
            &quot;Sem estágio&quot; e permanecem no sistema.
          </p>
        </CardContent>
      </Card>

      <StageFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        stage={editStage}
        nextOrder={nextOrder}
      />
    </div>
  );
}
