import { createContext, useContext, useMemo, useState } from "react";

type SessionContextValue = {
  sessionToken: string | null;
  setSessionToken: (token: string | null) => void;
};

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

function getInitialToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem("jmd-session-token");
}

export function SessionProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const [sessionToken, setSessionTokenState] = useState<string | null>(getInitialToken);

  const value = useMemo(
    () => ({
      sessionToken,
      setSessionToken: (token: string | null) => {
        setSessionTokenState(token);
        if (typeof window !== "undefined") {
          if (token) {
            window.localStorage.setItem("jmd-session-token", token);
          } else {
            window.localStorage.removeItem("jmd-session-token");
          }
        }
      },
    }),
    [sessionToken],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionContextValue {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
