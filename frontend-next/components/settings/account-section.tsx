"use client";

import { User, Mail, Shield, Building2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/store/auth.store";

const ROLE_LABELS: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  admin:   { label: "Administrador", variant: "default" },
  manager: { label: "Gerente",       variant: "secondary" },
  sales:   { label: "Vendas",        variant: "outline" },
};

function initials(name: string) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-3 py-3 border-b border-border last:border-0">
      <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground">{label}</p>
        <div className="text-sm font-medium mt-0.5">{value}</div>
      </div>
    </div>
  );
}

export function AccountSection() {
  const { user } = useAuthStore();

  if (!user) return null;

  const roleInfo = ROLE_LABELS[user.role] ?? { label: user.role, variant: "outline" as const };

  return (
    <div className="space-y-5 max-w-lg">
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-base">Perfil</CardTitle>
          <CardDescription>Informações da sua conta</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Avatar + name */}
          <div className="flex items-center gap-4 pb-4 mb-1 border-b border-border">
            <Avatar className="h-14 w-14">
              <AvatarFallback className="text-lg font-bold bg-primary text-primary-foreground">
                {initials(user.name)}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold text-base">{user.name}</p>
              <Badge variant={roleInfo.variant} className="mt-1 text-xs">
                {roleInfo.label}
              </Badge>
            </div>
          </div>

          <InfoRow
            icon={Mail}
            label="E-mail"
            value={<span className="font-mono text-xs">{user.email}</span>}
          />
          <InfoRow
            icon={Shield}
            label="Função"
            value={<Badge variant={roleInfo.variant}>{roleInfo.label}</Badge>}
          />
          <InfoRow
            icon={Building2}
            label="Workspace ID"
            value={<span className="font-mono text-xs">#{user.workspace_id}</span>}
          />
          <InfoRow
            icon={User}
            label="ID do usuário"
            value={<span className="font-mono text-xs">#{user.id}</span>}
          />
        </CardContent>
      </Card>

      <Card className="border-dashed bg-muted/20">
        <CardContent className="pt-4 pb-3">
          <p className="text-xs text-muted-foreground">
            Para alterar senha ou dados da conta, entre em contato com o administrador
            do workspace.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
