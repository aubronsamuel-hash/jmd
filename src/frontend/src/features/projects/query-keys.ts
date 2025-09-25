export const projectsKeys = {
  all: ["projects"] as const,
  list: () => [...projectsKeys.all, "list"] as const,
  detail: (projectId: string) => [...projectsKeys.all, "detail", projectId] as const,
};
