import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectsListPage } from "./projects-list-page";
import { renderWithProviders } from "@/test-utils";

const venuesResponse = [
  {
    id: "venue-1",
    name: "Théâtre Municipal",
    organizationId: "org-1",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const projectsResponse = [
  {
    id: "project-1",
    name: "Festival d'été",
    description: "Édition 2025",
    startDate: "2025-06-01",
    endDate: "2025-06-30",
    budgetCents: 1500000,
    teamType: "Technique",
    organizationId: "org-1",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    venues: venuesResponse,
  },
];

describe("ProjectsListPage", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("affiche la table des projets et permet la création", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/api/projects") && (!init || init.method === "GET")) {
        return Promise.resolve(
          new Response(JSON.stringify(projectsResponse), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      if (url.endsWith("/api/venues")) {
        return Promise.resolve(
          new Response(JSON.stringify(venuesResponse), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      if (url.endsWith("/api/projects") && init?.method === "POST") {
        const body = init.body ? JSON.parse(init.body as string) : {};
        return Promise.resolve(
          new Response(JSON.stringify({ ...projectsResponse[0], id: "project-2", ...body }), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      return Promise.reject(new Error(`Unhandled request: ${url}`));
    });
    vi.stubGlobal("fetch", fetchMock);

    const { queryClient } = renderWithProviders(<ProjectsListPage />, {
      initialEntries: ["/projects"],
    });

    expect(await screen.findByText("Projets")).toBeInTheDocument();
    expect(await screen.findByRole("link", { name: "Festival d'été" })).toBeInTheDocument();
    const venueLabels = await screen.findAllByText("Théâtre Municipal");
    expect(venueLabels.length).toBeGreaterThan(0);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nom du projet"), "Nouveau projet");
    await user.click(screen.getByRole("button", { name: "Créer" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:3000/api/projects",
        expect.objectContaining({ method: "POST" }),
      );
    });

    await waitFor(() => {
      expect(queryClient.isFetching()).toBe(0);
    });

    await waitFor(() => {
      expect(queryClient.isMutating()).toBe(0);
    });
  });
});
