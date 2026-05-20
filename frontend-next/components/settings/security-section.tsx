"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Eye, EyeOff, Save, CheckCircle2, AlertCircle, User, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { settingsService } from "@/services/settings.service";
import { useAuthStore } from "@/store/auth.store";

function PasswordInput({
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
        className="pr-9"
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

export function SecuritySection() {
  const { user, setUser } = useAuthStore();

  // Profile / name
  const [name, setName] = useState(user?.name ?? "");
  const [nameSaved, setNameSaved] = useState(false);

  // Password
  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [pwdSaved, setPwdSaved] = useState(false);
  const [pwdError, setPwdError] = useState("");

  const profileMutation = useMutation({
    mutationFn: (n: string) => settingsService.updateProfile({ name: n }),
    onSuccess: (updated) => {
      setUser(updated);
      setNameSaved(true);
      setTimeout(() => setNameSaved(false), 3000);
    },
  });

  const passwordMutation = useMutation({
    mutationFn: () =>
      settingsService.updateProfile({ current_password: currentPwd, new_password: newPwd }),
    onSuccess: () => {
      setCurrentPwd("");
      setNewPwd("");
      setConfirmPwd("");
      setPwdError("");
      setPwdSaved(true);
      setTimeout(() => setPwdSaved(false), 3000);
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setPwdError(err?.response?.data?.detail ?? "Erro ao atualizar senha");
    },
  });

  function handleNameSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    profileMutation.mutate(name.trim());
  }

  function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPwdError("");
    if (newPwd.length < 6) {
      setPwdError("A nova senha deve ter pelo menos 6 caracteres");
      return;
    }
    if (newPwd !== confirmPwd) {
      setPwdError("As senhas não coincidem");
      return;
    }
    passwordMutation.mutate();
  }

  return (
    <div className="space-y-5 max-w-lg">
      {/* Name */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <User className="h-4 w-4" />
            Dados pessoais
          </CardTitle>
          <CardDescription>Altere seu nome de exibição no sistema</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleNameSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="profile-name">Nome</Label>
              <Input
                id="profile-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Seu nome completo"
              />
            </div>
            <div className="flex items-center justify-between">
              {nameSaved ? (
                <p className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" />
                  Nome atualizado
                </p>
              ) : profileMutation.isError ? (
                <p className="text-xs text-destructive">Erro ao salvar nome</p>
              ) : (
                <span />
              )}
              <Button type="submit" size="sm" disabled={profileMutation.isPending || !name.trim()}>
                <Save className="h-3.5 w-3.5" />
                {profileMutation.isPending ? "Salvando..." : "Salvar"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Password */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Lock className="h-4 w-4" />
            Alterar senha
          </CardTitle>
          <CardDescription>Informe a senha atual para criar uma nova</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cur-pwd">Senha atual</Label>
              <PasswordInput
                id="cur-pwd"
                placeholder="Sua senha atual"
                value={currentPwd}
                onChange={setCurrentPwd}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-pwd">Nova senha</Label>
              <PasswordInput
                id="new-pwd"
                placeholder="Mínimo 6 caracteres"
                value={newPwd}
                onChange={setNewPwd}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-pwd">Confirmar nova senha</Label>
              <PasswordInput
                id="confirm-pwd"
                placeholder="Repita a nova senha"
                value={confirmPwd}
                onChange={setConfirmPwd}
              />
            </div>

            {pwdError && (
              <p className="text-xs text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {pwdError}
              </p>
            )}

            <div className="flex items-center justify-between">
              {pwdSaved ? (
                <p className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" />
                  Senha atualizada com sucesso
                </p>
              ) : (
                <span />
              )}
              <Button
                type="submit"
                size="sm"
                disabled={
                  passwordMutation.isPending ||
                  !currentPwd ||
                  !newPwd ||
                  !confirmPwd
                }
              >
                <Save className="h-3.5 w-3.5" />
                {passwordMutation.isPending ? "Salvando..." : "Alterar senha"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
