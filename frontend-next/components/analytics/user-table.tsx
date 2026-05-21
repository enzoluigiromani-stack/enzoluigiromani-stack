"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ByUserResponse } from "@/types/analytics";

interface UserTableProps {
  data?: ByUserResponse;
  loading?: boolean;
}

function currency(v: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }).format(v);
}

function ConversionBadge({ rate }: { rate: number }) {
  const variant = rate >= 30 ? "default" : rate >= 15 ? "secondary" : "outline";
  return <Badge variant={variant} className="text-xs tabular-nums">{rate.toFixed(1)}%</Badge>;
}

export function UserTable({ data, loading }: UserTableProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Performance por Usuário</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const users = data?.users ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Performance por Usuário</CardTitle>
        <p className="text-xs text-muted-foreground">{data?.period_label}</p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuário</TableHead>
                <TableHead className="text-right">Leads</TableHead>
                <TableHead className="text-right">Convertidos</TableHead>
                <TableHead className="text-right">Conversão</TableHead>
                <TableHead className="text-right">Receita Fechada</TableHead>
                <TableHead className="text-right">Em Aberto</TableHead>
                <TableHead className="text-right">Tarefas ✓</TableHead>
                <TableHead className="text-right">Pendentes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.user_id}>
                  <TableCell>
                    <div>
                      <p className="font-medium text-sm">{u.user_name}</p>
                      <p className="text-xs text-muted-foreground">{u.user_email}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{u.leads_assigned}</TableCell>
                  <TableCell className="text-right tabular-nums text-emerald-600">{u.leads_converted}</TableCell>
                  <TableCell className="text-right">
                    <ConversionBadge rate={u.conversion_rate} />
                  </TableCell>
                  <TableCell className="text-right tabular-nums text-sm">{currency(u.closed_revenue)}</TableCell>
                  <TableCell className="text-right tabular-nums text-muted-foreground">{currency(u.estimated_revenue)}</TableCell>
                  <TableCell className="text-right tabular-nums text-emerald-600">{u.tasks_completed}</TableCell>
                  <TableCell className="text-right tabular-nums text-amber-600">{u.tasks_pending}</TableCell>
                </TableRow>
              ))}
              {users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                    Sem dados no período
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
