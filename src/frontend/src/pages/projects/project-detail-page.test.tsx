import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Route, Routes } from "react-router-dom";

import { ProjectDetailPage } from "./project-detail-page";
import { renderWithProviders } from "@/test-utils";

const projectResponse = {
  id: "project-1",
  name: "Tournée hiver",
  description: "Dates dans le sud",
  startDate: "2025-01-10",
  endDate: "2025-02-18",
  budgetCents: 2500000,
  teamType: "Production",
  organizationId: "org-1",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  venues: [
    {
      id: "venue-1",
      name: "Zénith",
      organizationId: "org-1",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ],
};

describe("ProjectDetailPage", () => {
  it("pré-remplit le formulaire et envoie une mise à jour", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/api/projects/project-1") && (!init || init.method === "GET")) {
        return Promise.resolve(
          new Response(JSON.stringify(projectResponse), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      if (url.endsWith("/api/venues")) {
        return Promise.resolve(
          new Response(JSON.stringify(projectResponse.venues), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      if (url.endsWith("/api/projects/project-1") && init?.method === "PUT") {
        return Promise.resolve(
          new Response(JSON.stringify({ ...projectResponse, name: "Tournée hiver 2025" }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        );
      }
      return Promise.reject(new Error(`Unhandled request: ${url}`));
    });
    vi.stubGlobal("fetch", fetchMock);

    renderWithProviders(
      <Routes>
        <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
      </Routes>,
      { initialEntries: ["/projects/project-1"] },
    );

    expect(await screen.findByDisplayValue("Tournée hiver")).toBeInTheDocument();
    const nameInput = screen.getByLabelText("Nom");
    await userEvent.clear(nameInput);
    await userEvent.type(nameInput, "Tournée hiver 2025");

    await userEvent.click(screen.getByRole("button", { name: "Enregistrer" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:3000/api/projects/project-1",
        expect.objectContaining({ method: "PUT" }),
      );
    });
  });
});
