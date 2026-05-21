"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import type { AnalyticsFilters } from "@/types/analytics";
import type { WorkspaceMember } from "@/types";

const PRESETS = [
  { label: "7d",  days: 7 },
  { label: "30d", days: 30 },
  { label: "90d", days: 90 },
  { label: "1a",  days: 365 },
] as const;

const SOURCES = [
  { key: "meta_ads",  label: "Meta Ads" },
  { key: "instagram", label: "Instagram" },
  { key: "whatsapp",  label: "WhatsApp" },
  { key: "google",    label: "Google" },
  { key: "referral",  label: "Indicação" },
  { key: "organic",   label: "Orgânico" },
] as const;

interface AnalyticsFiltersProps {
  filters: AnalyticsFilters;
  members?: WorkspaceMember[];
  onChange: (filters: AnalyticsFilters) => void;
}

function toDateStr(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function AnalyticsFiltersBar({ filters, members = [], onChange }: AnalyticsFiltersProps) {
  const [activePreset, setActivePreset] = useState<number | null>(30);

  function applyPreset(days: number) {
    const to = new Date();
    const from = new Date();
    from.setDate(from.getDate() - days);
    setActivePreset(days);
    onChange({ ...filters, date_from: toDateStr(from), date_to: toDateStr(to) });
  }

  function handleDate(key: "date_from" | "date_to", val: string) {
    setActivePreset(null);
    onChange({ ...filters, [key]: val || undefined });
  }

  function handleUser(val: string) {
    onChange({ ...filters, user_id: val ? Number(val) : undefined });
  }

  function handleSource(val: string) {
    onChange({ ...filters, source: val || undefined });
  }

  function clear() {
    setActivePreset(null);
    onChange({});
  }

  return (
    <div className="flex flex-wrap items-end gap-3 pb-2">
      {/* Presets */}
      <div className="flex items-center gap-1">
        {PRESETS.map((p) => (
          <Button
            key={p.days}
            variant="outline"
            size="sm"
            className={cn("h-8 px-3 text-xs", activePreset === p.days && "bg-primary text-primary-foreground border-primary")}
            onClick={() => applyPreset(p.days)}
          >
            {p.label}
          </Button>
        ))}
      </div>

      {/* Custom range */}
      <div className="flex items-end gap-2">
        <div className="flex flex-col gap-1">
          <Label className="text-xs text-muted-foreground">De</Label>
          <Input
            type="date"
            className="h-8 text-xs w-36"
            value={filters.date_from ?? ""}
            onChange={(e) => handleDate("date_from", e.target.value)}
          />
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-xs text-muted-foreground">Até</Label>
          <Input
            type="date"
            className="h-8 text-xs w-36"
            value={filters.date_to ?? ""}
            onChange={(e) => handleDate("date_to", e.target.value)}
          />
        </div>
      </div>

      {/* Source */}
      <div className="flex flex-col gap-1">
        <Label className="text-xs text-muted-foreground">Origem</Label>
        <select
          className="h-8 text-xs border rounded-md px-2 bg-background text-foreground min-w-[120px]"
          value={filters.source ?? ""}
          onChange={(e) => handleSource(e.target.value)}
        >
          <option value="">Todas</option>
          {SOURCES.map((s) => (
            <option key={s.key} value={s.key}>{s.label}</option>
          ))}
        </select>
      </div>

      {/* User */}
      {members.length > 0 && (
        <div className="flex flex-col gap-1">
          <Label className="text-xs text-muted-foreground">Usuário</Label>
          <select
            className="h-8 text-xs border rounded-md px-2 bg-background text-foreground min-w-[130px]"
            value={filters.user_id ?? ""}
            onChange={(e) => handleUser(e.target.value)}
          >
            <option value="">Todos</option>
            {members.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>
      )}

      <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={clear}>
        Limpar
      </Button>
    </div>
  );
}
