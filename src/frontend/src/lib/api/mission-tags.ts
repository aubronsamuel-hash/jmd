import { ApiClient } from "./client";
import type { MissionTag } from "./types";

export function createMissionTagsApi(client: ApiClient) {
  return {
    list: () => client.request<MissionTag[]>({ path: "/mission-tags" }),
  };
}
