export const missionTemplateKeys = {
  all: ["mission-templates"] as const,
  list: () => [...missionTemplateKeys.all, "list"] as const,
};
