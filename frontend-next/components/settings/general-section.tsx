"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, CheckCircle2, Building2, Globe, DollarSign, Palette } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { settingsService } from "@/services/settings.service";
import type { WorkspaceSettings, WorkspaceSettingsUpdate } from "@/types";
import { cn } from "@/lib/utils";

const CURRENCIES = [
  { value: "BRL", label: "Real Brasileiro (R$)" },
  { value: "USD", label: "Dólar Americano ($)" },
  { value: "EUR", label: "Euro (€)" },
  { value: "GBP", label: "Libra Esterlina (£)" },
];

const TIMEZONES = [
  { value: "America/Sao_Paulo", label: "Brasília (UTC-3)" },
  { value: "America/Manaus", label: "Manaus (UTC-4)" },
  { value: "America/Belem", label: "Belém (UTC-3)" },
  { value: "America/New_York", label: "Nova York (UTC-5)" },
  { value: "America/Los_Angeles", label: "Los Angeles (UTC-8)" },
  { value: "Europe/London", label: "Londres (UTC+0)" },
  { value: "Europe/Lisbon", label: "Lisboa (UTC+0)" },
];

const PRESET_COLORS = [
  "#6366f1", "#8b5cf6", "#ec4899", "#ef4444",
  "#f97316", "#eab308", "#22c55e", "#06b6d4",
  "#3b82f6", "#64748b",
];

function SelectField({
  label,
  id,
  value,
  onChange,
  options,
  icon: Icon,
}: {
  label: string;
  id: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  icon: React.ElementType;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="flex items-center gap-1.5">
        <Icon className="h-3.5 w-3.5 text-muted-foreground" />
        {label}
      </Label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function GeneralSection() {
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState<WorkspaceSettingsUpdate>({
    company_name: "",
    currency: "BRL",
    timezone: "America/Sao_Paulo",
    primary_color: "#6366f1",
  });

  const { data: settings, isLoading } = useQuery<WorkspaceSettings>({
    queryKey: ["workspace-settings"],
    queryFn: settingsService.getSettings,
    retry: false,
  });

  const { data: workspace } = useQuery({
    queryKey: ["workspace"],
    queryFn: settingsService.getWorkspace,
  });

  useEffect(() => {
    if (settings) {
      setForm({
        company_name: settings.company_name ?? "",
        currency: settings.currency,
        timezone: settings.timezone,
        primary_color: settings.primary_color,
      });
    }
  }, [settings]);

  const mutation = useMutation({
    mutationFn: settingsService.updateSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(["workspace-settings"], data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate(form);
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-muted/50 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Workspace info */}
      {workspace && (
        <Card className="border-dashed">
          <CardContent className="pt-4 pb-3">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <Building2 className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-sm">{workspace.name}</p>
                <p className="text-xs text-muted-foreground">
                  Slug: <code className="font-mono">{workspace.slug}</code>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Identidade da Empresa</CardTitle>
          <CardDescription>Nome exibido em relatórios e comunicações</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="company_name" className="flex items-center gap-1.5">
              <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
              Nome da empresa
            </Label>
            <Input
              id="company_name"
              placeholder="Minha Empresa Ltda."
              value={form.company_name ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, company_name: e.target.value }))}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Localização e Moeda</CardTitle>
          <CardDescription>Afeta formatação de valores e horários</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <SelectField
            label="Moeda"
            id="currency"
            value={form.currency ?? "BRL"}
            onChange={(v) => setForm((f) => ({ ...f, currency: v }))}
            options={CURRENCIES}
            icon={DollarSign}
          />
          <SelectField
            label="Fuso horário"
            id="timezone"
            value={form.timezone ?? "America/Sao_Paulo"}
            onChange={(v) => setForm((f) => ({ ...f, timezone: v }))}
            options={TIMEZONES}
            icon={Globe}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Aparência</CardTitle>
          <CardDescription>Cor de destaque do sistema</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Label className="flex items-center gap-1.5">
            <Palette className="h-3.5 w-3.5 text-muted-foreground" />
            Cor principal
          </Label>
          <div className="flex items-center gap-3 flex-wrap">
            {PRESET_COLORS.map((color) => (
              <button
                key={color}
                type="button"
                title={color}
                onClick={() => setForm((f) => ({ ...f, primary_color: color }))}
                className={cn(
                  "h-7 w-7 rounded-full transition-all duration-150 shrink-0",
                  form.primary_color === color
                    ? "ring-2 ring-offset-2 ring-foreground scale-110"
                    : "hover:scale-110"
                )}
                style={{ backgroundColor: color }}
              />
            ))}
            <div className="flex items-center gap-2 ml-1">
              <input
                type="color"
                value={form.primary_color ?? "#6366f1"}
                onChange={(e) => setForm((f) => ({ ...f, primary_color: e.target.value }))}
                className="h-7 w-7 rounded-full cursor-pointer border border-border p-0 bg-transparent"
                title="Cor personalizada"
              />
              <span className="text-xs text-muted-foreground font-mono">
                {form.primary_color}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="flex items-center justify-between pt-1">
        {saved ? (
          <p className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4" />
            Configurações salvas
          </p>
        ) : (
          <span />
        )}
        <Button type="submit" disabled={mutation.isPending}>
          <Save className="h-4 w-4" />
          {mutation.isPending ? "Salvando..." : "Salvar alterações"}
        </Button>
      </div>

      {mutation.isError && (
        <p className="text-sm text-destructive">
          Erro ao salvar. Verifique suas permissões.
        </p>
      )}
    </form>
  );
}
