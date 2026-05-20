"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Copy,
  Check,
  Eye,
  EyeOff,
  Save,
  CheckCircle2,
  AlertCircle,
  Webhook,
  MessageCircle,
  Mail,
  Smartphone,
  BarChart2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { settingsService } from "@/services/settings.service";
import type { WorkspaceIntegrations, WorkspaceIntegrationsUpdate } from "@/types";
import { cn } from "@/lib/utils";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Helpers ───────────────────────────────────────────────────────────────────

function SecretInput({
  id,
  placeholder,
  value,
  onChange,
}: {
  id: string;
  placeholder?: string;
  value: string;
  onChange: (v: string) => void;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <Input
        id={id}
        type={show ? "text" : "password"}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pr-9 font-mono text-sm"
      />
      <button
        type="button"
        tabIndex={-1}
        onClick={() => setShow((s) => !s)}
        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
      >
        {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  function handleCopy() {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }
  return (
    <Button type="button" variant="outline" size="sm" onClick={handleCopy} className="shrink-0">
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? "Copiado" : "Copiar"}
    </Button>
  );
}

function hasValue(...values: (string | undefined | null)[]): boolean {
  return values.some((v) => v && v.trim().length > 0);
}

// ── Integration Card ──────────────────────────────────────────────────────────

interface IntCardProps {
  icon: React.ElementType;
  title: string;
  description: string;
  configured: boolean;
  onSave: () => void;
  isPending: boolean;
  isError: boolean;
  isSaved: boolean;
  errorMessage?: string;
  children: React.ReactNode;
}

function IntegrationCard({
  icon: Icon,
  title,
  description,
  configured,
  onSave,
  isPending,
  isError,
  isSaved,
  errorMessage,
  children,
}: IntCardProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
              <Icon className="h-4 w-4 text-muted-foreground" />
            </div>
            <div>
              <CardTitle className="text-sm flex items-center gap-2">
                {title}
                {configured && (
                  <Badge variant="outline" className="text-[10px] text-emerald-600 border-emerald-200 bg-emerald-50 dark:bg-emerald-950 dark:border-emerald-800">
                    Configurado
                  </Badge>
                )}
              </CardTitle>
              <CardDescription className="text-xs">{description}</CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {children}

          {isError && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              {errorMessage ?? "Erro ao salvar"}
            </p>
          )}

          <div className="flex items-center justify-between pt-1">
            {isSaved ? (
              <p className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" />
                Salvo
              </p>
            ) : <span />}
            <Button type="button" size="sm" onClick={onSave} disabled={isPending}>
              <Save className="h-3.5 w-3.5" />
              {isPending ? "Salvando..." : "Salvar"}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── IntegrationsSection ───────────────────────────────────────────────────────

export function IntegrationsSection() {
  const queryClient = useQueryClient();

  const { data: integrations, isLoading } = useQuery<WorkspaceIntegrations>({
    queryKey: ["integrations"],
    queryFn: settingsService.getIntegrations,
  });

  const { data: workspace } = useQuery({
    queryKey: ["workspace"],
    queryFn: settingsService.getWorkspace,
  });

  // Local form state — initialized from server data
  const [form, setForm] = useState<WorkspaceIntegrationsUpdate>({});
  const [savedKey, setSavedKey] = useState<string | null>(null);
  const [errorKey, setErrorKey] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (integrations) {
      setForm({
        whatsapp_token:    integrations.whatsapp_token    ?? "",
        whatsapp_phone_id: integrations.whatsapp_phone_id ?? "",
        meta_access_token: integrations.meta_access_token ?? "",
        meta_pixel_id:     integrations.meta_pixel_id     ?? "",
        sendgrid_api_key:    integrations.sendgrid_api_key    ?? "",
        sendgrid_from_email: integrations.sendgrid_from_email ?? "",
        twilio_account_sid:  integrations.twilio_account_sid  ?? "",
        twilio_auth_token:   integrations.twilio_auth_token   ?? "",
        twilio_from_number:  integrations.twilio_from_number  ?? "",
      });
    }
  }, [integrations]);

  const [pendingKey, setPendingKey] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: WorkspaceIntegrationsUpdate) =>
      settingsService.updateIntegrations(payload),
  });

  function save(key: string, fields: Partial<WorkspaceIntegrationsUpdate>) {
    setSavedKey(null);
    setErrorKey(null);
    setPendingKey(key);
    mutation.mutate(fields, {
      onSuccess: (data) => {
        queryClient.setQueryData(["integrations"], data);
        setPendingKey(null);
        setSavedKey(key);
        setTimeout(() => setSavedKey(null), 3000);
      },
      onError: (err: unknown) => {
        setPendingKey(null);
        setErrorKey(key);
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        setErrorMsg(detail ?? "Erro ao salvar");
      },
    });
  }

  const f = (field: keyof WorkspaceIntegrationsUpdate) =>
    (form[field] as string) ?? "";

  const set = (field: keyof WorkspaceIntegrationsUpdate) =>
    (v: string) => setForm((prev) => ({ ...prev, [field]: v }));

  const webhookUrl = workspace
    ? `${BASE_URL}/webhook/leads/${workspace.slug}`
    : "";

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-muted/50 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Webhook URL */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
              <Webhook className="h-4 w-4 text-muted-foreground" />
            </div>
            <div>
              <CardTitle className="text-sm">URL de captura de leads</CardTitle>
              <CardDescription className="text-xs">
                Endpoint público para receber leads via webhook (Meta Ads, formulários, etc.)
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">POST</Label>
            <div className="flex items-center gap-2">
              <Input
                readOnly
                value={webhookUrl}
                className="font-mono text-xs bg-muted/40"
              />
              {webhookUrl && <CopyButton text={webhookUrl} />}
            </div>
            <p className="text-xs text-muted-foreground">
              Configure este URL como destino no seu gerenciador de anúncios ou formulário externo.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* WhatsApp */}
      <IntegrationCard
        icon={MessageCircle}
        title="WhatsApp Business API"
        description="Token e número para envio de mensagens via WhatsApp"
        configured={hasValue(integrations?.whatsapp_token, integrations?.whatsapp_phone_id)}
        onSave={() =>
          save("whatsapp", {
            whatsapp_token: f("whatsapp_token"),
            whatsapp_phone_id: f("whatsapp_phone_id"),
          })
        }
        isPending={pendingKey === "whatsapp"}
        isError={errorKey === "whatsapp"}
        isSaved={savedKey === "whatsapp"}
        errorMessage={errorMsg}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="wa-token" className="text-xs">Token de acesso</Label>
            <SecretInput
              id="wa-token"
              placeholder="EAAxxxxxxx..."
              value={f("whatsapp_token")}
              onChange={set("whatsapp_token")}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="wa-phone" className="text-xs">Phone Number ID</Label>
            <Input
              id="wa-phone"
              placeholder="1234567890"
              value={f("whatsapp_phone_id")}
              onChange={(e) => set("whatsapp_phone_id")(e.target.value)}
              className="font-mono text-sm"
            />
          </div>
        </div>
      </IntegrationCard>

      {/* Meta */}
      <IntegrationCard
        icon={BarChart2}
        title="Meta / Facebook Ads"
        description="Access token e Pixel ID para captura de leads do Meta Lead Ads"
        configured={hasValue(integrations?.meta_access_token, integrations?.meta_pixel_id)}
        onSave={() =>
          save("meta", {
            meta_access_token: f("meta_access_token"),
            meta_pixel_id: f("meta_pixel_id"),
          })
        }
        isPending={pendingKey === "meta"}
        isError={errorKey === "meta"}
        isSaved={savedKey === "meta"}
        errorMessage={errorMsg}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="meta-token" className="text-xs">Access Token</Label>
            <SecretInput
              id="meta-token"
              placeholder="EAAxxxxxxx..."
              value={f("meta_access_token")}
              onChange={set("meta_access_token")}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="meta-pixel" className="text-xs">Pixel ID</Label>
            <Input
              id="meta-pixel"
              placeholder="123456789"
              value={f("meta_pixel_id")}
              onChange={(e) => set("meta_pixel_id")(e.target.value)}
              className="font-mono text-sm"
            />
          </div>
        </div>
      </IntegrationCard>

      {/* E-mail */}
      <IntegrationCard
        icon={Mail}
        title="E-mail via SendGrid"
        description="API key e remetente padrão para envio de e-mails"
        configured={hasValue(integrations?.sendgrid_api_key, integrations?.sendgrid_from_email)}
        onSave={() =>
          save("email", {
            sendgrid_api_key: f("sendgrid_api_key"),
            sendgrid_from_email: f("sendgrid_from_email"),
          })
        }
        isPending={pendingKey === "email"}
        isError={errorKey === "email"}
        isSaved={savedKey === "email"}
        errorMessage={errorMsg}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="sg-key" className="text-xs">API Key</Label>
            <SecretInput
              id="sg-key"
              placeholder="SG.xxxxxxx..."
              value={f("sendgrid_api_key")}
              onChange={set("sendgrid_api_key")}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="sg-from" className="text-xs">E-mail remetente</Label>
            <Input
              id="sg-from"
              type="email"
              placeholder="noreply@empresa.com"
              value={f("sendgrid_from_email")}
              onChange={(e) => set("sendgrid_from_email")(e.target.value)}
              className="font-mono text-sm"
            />
          </div>
        </div>
      </IntegrationCard>

      {/* SMS */}
      <IntegrationCard
        icon={Smartphone}
        title="SMS via Twilio"
        description="Credenciais Twilio para envio de mensagens SMS"
        configured={hasValue(integrations?.twilio_account_sid, integrations?.twilio_auth_token)}
        onSave={() =>
          save("sms", {
            twilio_account_sid: f("twilio_account_sid"),
            twilio_auth_token: f("twilio_auth_token"),
            twilio_from_number: f("twilio_from_number"),
          })
        }
        isPending={pendingKey === "sms"}
        isError={errorKey === "sms"}
        isSaved={savedKey === "sms"}
        errorMessage={errorMsg}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="tw-sid" className="text-xs">Account SID</Label>
            <SecretInput
              id="tw-sid"
              placeholder="ACxxxxxxx..."
              value={f("twilio_account_sid")}
              onChange={set("twilio_account_sid")}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="tw-token" className="text-xs">Auth Token</Label>
            <SecretInput
              id="tw-token"
              placeholder="Token secreto"
              value={f("twilio_auth_token")}
              onChange={set("twilio_auth_token")}
            />
          </div>
          <div className="space-y-1.5 sm:col-span-2">
            <Label htmlFor="tw-from" className="text-xs">Número remetente</Label>
            <Input
              id="tw-from"
              placeholder="+5511999999999"
              value={f("twilio_from_number")}
              onChange={(e) => set("twilio_from_number")(e.target.value)}
              className={cn("font-mono text-sm", "sm:max-w-[200px]")}
            />
          </div>
        </div>
      </IntegrationCard>
    </div>
  );
}
