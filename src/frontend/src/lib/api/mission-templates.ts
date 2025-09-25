import { ApiClient } from "./client";
import type { MissionTemplate, MissionTemplateCreate, MissionTemplateUpdate } from "./types";

export function createMissionTemplatesApi(client: ApiClient) {
  return {
    list: () => client.request<MissionTemplate[]>({ path: "/mission-templates" }),
    create: (payload: MissionTemplateCreate) =>
      client.request<MissionTemplate, MissionTemplateCreate>({
        path: "/mission-templates",
        method: "POST",
        body: payload,
      }),
    update: (missionTemplateId: string, payload: MissionTemplateUpdate) =>
      client.request<MissionTemplate, MissionTemplateUpdate>({
        path: `/mission-templates/${missionTemplateId}`,
        method: "PUT",
        body: payload,
      }),
    remove: (missionTemplateId: string) =>
      client.request<void>({ path: `/mission-templates/${missionTemplateId}`, method: "DELETE" }),
  };
}
