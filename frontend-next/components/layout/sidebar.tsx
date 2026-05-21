"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  CheckSquare,
  BarChart2,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
  Kanban,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/ui.store";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/theme-toggle";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/leads",     label: "Leads",     icon: Users },
  { href: "/pipeline",  label: "Pipeline",  icon: Kanban },
  { href: "/inbox",     label: "Inbox",     icon: MessageSquare },
  { href: "/tasks",     label: "Tarefas",   icon: CheckSquare },
  { href: "/reports",   label: "Relatórios", icon: BarChart2 },
];

const bottomItems = [
  { href: "/automations", label: "Automações",    icon: Zap },
  { href: "/settings",    label: "Configurações", icon: Settings },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-card border-r border-border transition-all duration-300 shrink-0",
        sidebarCollapsed ? "w-16" : "w-60"
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-border">
        {!sidebarCollapsed && (
          <span className="text-lg font-bold text-primary truncate">CRM Agência</span>
        )}
        <Button
          variant="ghost"
          size="icon"
          className={cn("ml-auto shrink-0", sidebarCollapsed && "mx-auto")}
          onClick={toggleSidebar}
        >
          {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {/* Main nav */}
      <nav className="flex-1 overflow-y-auto py-4 space-y-0.5 px-2">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!sidebarCollapsed && <span className="truncate">{label}</span>}
            </Link>
          );
        })}
      </nav>

      <Separator />

      {/* Bottom nav */}
      <nav className="py-3 space-y-0.5 px-2">
        {bottomItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!sidebarCollapsed && <span className="truncate">{label}</span>}
            </Link>
          );
        })}

        {/* Theme toggle at the bottom of sidebar */}
        {!sidebarCollapsed && (
          <div className="flex items-center gap-2 px-3 py-2">
            <ThemeToggle className="h-8 w-8 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Tema</span>
          </div>
        )}
      </nav>
    </aside>
  );
}
