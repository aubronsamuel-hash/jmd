import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";

import { ApiProvider } from "@/features/shared/api-provider";
import { SessionProvider } from "@/providers/session-provider";
import { ThemeProvider } from "@/providers/theme-provider";

export function renderWithProviders(ui: ReactNode, { initialEntries = ["/"] } = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  window.localStorage.clear();
  window.localStorage.setItem("jmd-session-token", "test-token");

  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <SessionProvider>
        <ThemeProvider>
          <QueryClientProvider client={queryClient}>
            <ApiProvider>{ui}</ApiProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </SessionProvider>
    </MemoryRouter>,
  );
}
