"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";
import { useTheme } from "@/hooks/use-theme";

const PREVIEW_CLASSES = {
  light:  "bg-white border-gray-200 text-gray-900",
  dark:   "bg-[#121212] border-[#2e2e2e] text-[#ededed]",
  system: "bg-gradient-to-br from-white to-[#121212] border-gray-400 text-gray-500",
};

export function AppearanceSection() {
  const { theme, resolvedTheme } = useTheme();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Aparência</CardTitle>
          <p className="text-sm text-muted-foreground">
            Escolha entre tema claro, escuro ou sincronizado com o sistema operacional.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          <ThemeToggle variant="full" />

          {/* Preview */}
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
              Prévia — {resolvedTheme === "dark" ? "Escuro" : "Claro"}
            </p>
            <div
              className={`rounded-xl border p-4 space-y-3 transition-colors duration-300 ${
                PREVIEW_CLASSES[resolvedTheme as keyof typeof PREVIEW_CLASSES] ?? PREVIEW_CLASSES.light
              }`}
            >
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-blue-500" />
                <div
                  className={`h-2.5 w-24 rounded-full ${
                    resolvedTheme === "dark" ? "bg-[#2e2e2e]" : "bg-gray-200"
                  }`}
                />
              </div>
              <div className="flex gap-2">
                {[40, 24, 32].map((w, i) => (
                  <div
                    key={i}
                    className={`h-8 rounded-md ${
                      resolvedTheme === "dark" ? "bg-[#1a1a1a] border border-[#2e2e2e]" : "bg-gray-100 border border-gray-200"
                    }`}
                    style={{ width: `${w}%` }}
                  />
                ))}
              </div>
              <div
                className={`h-2 w-3/4 rounded-full ${
                  resolvedTheme === "dark" ? "bg-[#2e2e2e]" : "bg-gray-200"
                }`}
              />
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            A preferência é salva automaticamente e sincronizada entre sessões.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
