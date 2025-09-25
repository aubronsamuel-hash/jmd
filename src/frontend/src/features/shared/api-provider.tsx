import { createContext, useContext, useMemo } from "react";

import { createMissionTagsApi } from "@/lib/api/mission-tags";
import { createMissionTemplatesApi } from "@/lib/api/mission-templates";
import { createProjectsApi } from "@/lib/api/projects";
import { ApiClient } from "@/lib/api/client";
import { createVenuesApi } from "@/lib/api/venues";
import { useSession } from "@/providers/session-provider";

const ApiContext = createContext<ReturnType<typeof buildApiSuite> | undefined>(undefined);

function buildApiSuite(client: ApiClient) {
  return {
    client,
    projects: createProjectsApi(client),
    missionTemplates: createMissionTemplatesApi(client),
    missionTags: createMissionTagsApi(client),
    venues: createVenuesApi(client),
  };
}

export function ApiProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const { sessionToken } = useSession();
  const api = useMemo(() => {
    const client = new ApiClient({
      getSessionToken: () => sessionToken,
    });
    return buildApiSuite(client);
  }, [sessionToken]);

  return <ApiContext.Provider value={api}>{children}</ApiContext.Provider>;
}

export function useApi() {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error("useApi must be used within an ApiProvider");
  }
  return context;
}
