import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MissionTemplatesPage } from "./mission-templates-page";
import { renderWithProviders } from "@/test-utils";

const venuesResponse = [
  {
    id: "venue-1",
    name: "Salle Polyvalente",
    organizationId: "org-1",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const tagsResponse = [
  {
    id: "tag-1",
    slug: "regie",
    label: "Régie",
    organizationId: "org-1",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const templatesResponse = [
  {
    id: "template-1",
    name: "Balance son",
    description: "Préparation avant spectacle",
    teamSize: 3,
    requiredSkills: ["Son", "Lumière"],
    defaultStartTime: "16:00:00",
    defaultEndTime: "18:00:00",
    defaultVenueId: "venue-1",
    defaultVenue: venuesResponse[0],
    tags: tagsResponse,
    organizationId: "org-1",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

describe("MissionTemplatesPage", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("liste les gabarits existants et permet d'ouvrir l'éditeur inline", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/api/mission-templates") && (!init || init.method === "GET")) {
        return Promise.resolve(
          new Response(JSON.stringify(templatesResponse), {
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
      if (url.endsWith("/api/mission-tags")) {
        return Promise.resolve(
          new Response(JSON.stringify(tagsResponse), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      if (url.endsWith("/api/mission-templates") && init?.method === "POST") {
        return Promise.resolve(
          new Response(JSON.stringify(templatesResponse[0]), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      return Promise.reject(new Error(`Unhandled request: ${url}`));
    });
    vi.stubGlobal("fetch", fetchMock);

    renderWithProviders(<MissionTemplatesPage />, { initialEntries: ["/mission-templates"] });

    expect(await screen.findByText("Gabarits de mission")).toBeInTheDocument();
    expect(await screen.findByText("Balance son")).toBeInTheDocument();
    const tagBadges = await screen.findAllByText("Régie");
    expect(tagBadges.length).toBeGreaterThan(0);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Éditer" }));
    const editor = await screen.findByTestId("mission-template-editor-template-1");
    expect(within(editor).getByLabelText("Nom")).toHaveValue("Balance son");
  });
});
