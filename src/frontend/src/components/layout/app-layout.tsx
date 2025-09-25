import { NavLink } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useTheme } from "@/providers/theme-provider";
import { ApiProvider } from "@/features/shared/api-provider";

export function AppLayout({ children }: { children: React.ReactNode }): JSX.Element {
  const { theme, toggleTheme } = useTheme();

  return (
    <ApiProvider>
      <div className="flex min-h-screen flex-col bg-background text-foreground">
        <header className="border-b border-border bg-card/40 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <div className="flex items-center gap-6">
              <span className="text-xl font-semibold">JMD Planning</span>
              <nav className="flex items-center gap-4 text-sm font-medium">
                <NavLink
                  to="/projects"
                  className={({ isActive }) =>
                    isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
                  }
                >
                  Projets
                </NavLink>
                <NavLink
                  to="/mission-templates"
                  className={({ isActive }) =>
                    isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
                  }
                >
                  Gabarits de mission
                </NavLink>
              </nav>
            </div>
            <Button variant="outline" onClick={toggleTheme} aria-label="Basculer le thème">
              Mode {theme === "light" ? "sombre" : "clair"}
            </Button>
          </div>
        </header>
        <Separator />
        <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-6 py-8">
          {children}
        </main>
      </div>
    </ApiProvider>
  );
}
