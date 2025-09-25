import { useQuery } from "@tanstack/react-query";

import { useApi } from "@/features/shared/api-provider";

const missionTagKeys = {
  all: ["mission-tags"] as const,
  list: () => [...missionTagKeys.all, "list"] as const,
};

export function useMissionTags() {
  const { missionTags } = useApi();
  return useQuery({
    queryKey: missionTagKeys.list(),
    queryFn: () => missionTags.list(),
  });
}
