import { useTheme as useNextTheme } from "next-themes";

export type ThemeMode = "light" | "dark" | "system";

export function useTheme() {
  const { theme, setTheme, resolvedTheme, systemTheme } = useNextTheme();
  const isDark = resolvedTheme === "dark";

  // Colors for recharts (cannot read CSS vars from SVG context)
  const chartColors = {
    grid:    isDark ? "#2e2e2e" : "#e5e7eb",
    tick:    isDark ? "#8c8c8c" : "#6b7280",
    tooltip: isDark ? "#1a1a1a" : "#ffffff",
    border:  isDark ? "#2e2e2e" : "#e5e7eb",
    text:    isDark ? "#ededed" : "#111827",
  };

  return {
    theme: theme as ThemeMode | undefined,
    setTheme,
    resolvedTheme,
    systemTheme,
    isDark,
    chartColors,
  };
}
