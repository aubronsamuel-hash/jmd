import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { MissionTemplateCreate, MissionTemplateUpdate } from "@/lib/api/types";
import { useApi } from "@/features/shared/api-provider";
import { missionTemplateKeys } from "./query-keys";

export function useMissionTemplates() {
  const { missionTemplates } = useApi();
  return useQuery({
    queryKey: missionTemplateKeys.list(),
    queryFn: () => missionTemplates.list(),
  });
}

export function useCreateMissionTemplate() {
  const { missionTemplates } = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: MissionTemplateCreate) => missionTemplates.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: missionTemplateKeys.list() });
    },
  });
}

export function useUpdateMissionTemplate(missionTemplateId: string) {
  const { missionTemplates } = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: MissionTemplateUpdate) =>
      missionTemplates.update(missionTemplateId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: missionTemplateKeys.list() });
    },
  });
}

export function useDeleteMissionTemplate(missionTemplateId: string) {
  const { missionTemplates } = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => missionTemplates.remove(missionTemplateId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: missionTemplateKeys.list() });
    },
  });
}
