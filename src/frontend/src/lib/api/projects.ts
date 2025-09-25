import { ApiClient } from "./client";
import type { Project, ProjectCreate, ProjectUpdate } from "./types";

export function createProjectsApi(client: ApiClient) {
  return {
    list: () => client.request<Project[]>({ path: "/projects" }),
    retrieve: (projectId: string) => client.request<Project>({ path: `/projects/${projectId}` }),
    create: (payload: ProjectCreate) =>
      client.request<Project, ProjectCreate>({ path: "/projects", method: "POST", body: payload }),
    update: (projectId: string, payload: ProjectUpdate) =>
      client.request<Project, ProjectUpdate>({
        path: `/projects/${projectId}`,
        method: "PUT",
        body: payload,
      }),
    remove: (projectId: string) =>
      client.request<void>({ path: `/projects/${projectId}`, method: "DELETE" }),
  };
}
