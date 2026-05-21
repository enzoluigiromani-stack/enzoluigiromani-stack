"use client";

import { Sun, Moon, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "@/hooks/use-theme";
import { cn } from "@/lib/utils";

const MODES = [
  { key: "light",  label: "Claro",   Icon: Sun },
  { key: "dark",   label: "Escuro",  Icon: Moon },
  { key: "system", label: "Sistema", Icon: Monitor },
] as const;

interface ThemeToggleProps {
  variant?: "icon" | "full";
  className?: string;
}

export function ThemeToggle({ variant = "icon", className }: ThemeToggleProps) {
  const { theme, setTheme, isDark } = useTheme();

  if (variant === "full") {
    return (
      <div className={cn("grid grid-cols-3 gap-2", className)}>
        {MODES.map(({ key, label, Icon }) => (
          <button
            key={key}
            onClick={() => setTheme(key)}
            className={cn(
              "flex flex-col items-center gap-2 rounded-xl border-2 p-3 text-xs font-medium transition-all hover:bg-accent",
              theme === key
                ? "border-primary bg-primary/5 text-primary"
                : "border-border text-muted-foreground"
            )}
          >
            <Icon className="h-5 w-5" />
            {label}
          </button>
        ))}
      </div>
    );
  }

  const ActiveIcon = isDark ? Moon : Sun;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className={className}>
          <ActiveIcon className="h-5 w-5" />
          <span className="sr-only">Alternar tema</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {MODES.map(({ key, label, Icon }) => (
          <DropdownMenuItem
            key={key}
            onClick={() => setTheme(key)}
            className={cn(theme === key && "font-medium text-primary")}
          >
            <Icon className="mr-2 h-4 w-4" />
            {label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
