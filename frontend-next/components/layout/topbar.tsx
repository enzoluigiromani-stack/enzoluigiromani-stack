"use client";

import { Bell, LogOut, CheckCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/store/auth.store";
import { useNotifications } from "@/hooks/use-notifications";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

function initials(name: string) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

function NotificationBell() {
  const { notifications, unreadCount, markRead, markAllRead } = useNotifications();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <div className="flex items-center justify-between px-2 py-1.5">
          <DropdownMenuLabel className="p-0">Notificações</DropdownMenuLabel>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs gap-1"
              onClick={markAllRead}
            >
              <CheckCheck className="h-3 w-3" />
              Marcar todas
            </Button>
          )}
        </div>
        <DropdownMenuSeparator />
        {notifications.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-6">
            Sem notificações
          </p>
        ) : (
          <div className="max-h-80 overflow-y-auto">
            {notifications.slice(0, 20).map((n) => (
              <DropdownMenuItem
                key={n.id}
                className={cn(
                  "flex flex-col items-start gap-0.5 px-3 py-2 cursor-pointer",
                  !n.read && "bg-primary/5",
                )}
                onClick={() => !n.read && markRead(n.id)}
              >
                <div className="flex items-center gap-2 w-full">
                  <span className="text-sm font-medium flex-1 truncate">{n.title}</span>
                  {!n.read && <span className="h-1.5 w-1.5 rounded-full bg-primary shrink-0" />}
                </div>
                {n.message && (
                  <span className="text-xs text-muted-foreground truncate w-full">
                    {n.message}
                  </span>
                )}
              </DropdownMenuItem>
            ))}
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function Topbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <header className="flex items-center h-16 px-6 border-b border-border bg-card gap-4 shrink-0">
      <div className="flex-1" />

      <NotificationBell />

      <ThemeToggle />

      <div className="flex items-center gap-3">
        <Avatar className="h-8 w-8">
          <AvatarFallback className="text-xs bg-primary text-primary-foreground">
            {user ? initials(user.name) : "?"}
          </AvatarFallback>
        </Avatar>
        {user && (
          <div className="hidden md:block">
            <p className="text-sm font-medium leading-none">{user.name}</p>
            <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
          </div>
        )}
      </div>

      <Button variant="ghost" size="icon" onClick={handleLogout} title="Sair">
        <LogOut className="h-5 w-5" />
      </Button>
    </header>
  );
}
