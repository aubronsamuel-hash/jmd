import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { Project, ProjectCreate, ProjectUpdate } from "@/lib/api/types";
import { useApi } from "@/features/shared/api-provider";
import { projectsKeys } from "./query-keys";

export function useProjects() {
  const { projects } = useApi();
  return useQuery({
    queryKey: projectsKeys.list(),
    queryFn: () => projects.list(),
  });
}

export function useProject(projectId: string | undefined) {
  const { projects } = useApi();
  return useQuery({
    queryKey: projectId ? projectsKeys.detail(projectId) : projectsKeys.all,
    queryFn: () => {
      if (!projectId) {
        throw new Error("projectId is required");
      }
      return projects.retrieve(projectId);
    },
    enabled: Boolean(projectId),
  });
}

export function useCreateProject() {
  const { projects } = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectCreate) => projects.create(payload),
    onMutate: async (payload) => {
      await queryClient.cancelQueries({ queryKey: projectsKeys.list() });
      const previousProjects = queryClient.getQueryData<Project[]>(projectsKeys.list());
      if (previousProjects) {
        const optimisticProject: Project = {
          id: `optimistic-${Date.now()}`,
          name: payload.name,
          description: payload.description ?? null,
          startDate: payload.startDate ?? null,
          endDate: payload.endDate ?? null,
          budgetCents: payload.budgetCents ?? null,
          teamType: payload.teamType ?? null,
          organizationId: "optimistic",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          venues: [],
        };
        queryClient.setQueryData(projectsKeys.list(), [...previousProjects, optimisticProject]);
      }
      return { previousProjects };
    },
    onError: (_error, _payload, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(projectsKeys.list(), context.previousProjects);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: projectsKeys.list() });
    },
  });
}

export function useUpdateProject(projectId: string) {
  const { projects } = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectUpdate) => projects.update(projectId, payload),
    onMutate: async (payload) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: projectsKeys.list() }),
        queryClient.cancelQueries({ queryKey: projectsKeys.detail(projectId) }),
      ]);
      const previousList = queryClient.getQueryData<Project[]>(projectsKeys.list());
      const previousDetail = queryClient.getQueryData<Project>(projectsKeys.detail(projectId));
      if (previousList) {
        queryClient.setQueryData(
          projectsKeys.list(),
          previousList.map((project) =>
            project.id === projectId
              ? {
                  ...project,
                  ...payload,
                  updatedAt: new Date().toISOString(),
                }
              : project,
          ),
        );
      }
      if (previousDetail) {
        queryClient.setQueryData(projectsKeys.detail(projectId), {
          ...previousDetail,
          ...payload,
          updatedAt: new Date().toISOString(),
        });
      }
      return { previousList, previousDetail };
    },
    onError: (_error, _payload, context) => {
      if (context?.previousList) {
        queryClient.setQueryData(projectsKeys.list(), context.previousList);
      }
      if (context?.previousDetail) {
        queryClient.setQueryData(projectsKeys.detail(projectId), context.previousDetail);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: projectsKeys.list() });
      void queryClient.invalidateQueries({ queryKey: projectsKeys.detail(projectId) });
    },
  });
}

export function useDeleteProject(projectId: string) {
  const { projects } = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => projects.remove(projectId),
    onMutate: async () => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: projectsKeys.list() }),
        queryClient.cancelQueries({ queryKey: projectsKeys.detail(projectId) }),
      ]);
      const previousList = queryClient.getQueryData<Project[]>(projectsKeys.list());
      queryClient.setQueryData(
        projectsKeys.list(),
        previousList?.filter((project) => project.id !== projectId) ?? [],
      );
      return { previousList };
    },
    onError: (_error, _variables, context) => {
      if (context?.previousList) {
        queryClient.setQueryData(projectsKeys.list(), context.previousList);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: projectsKeys.list() });
    },
  });
}
