import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiClient, ApiError } from "./client";

declare global {
  interface Window {
    location: Location;
  }
}

describe("ApiClient", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("ajoute le header X-Session-Token lorsque disponible", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const client = new ApiClient({ getSessionToken: () => "token-123" });
    const result = await client.request<{ status: string }>({ path: "/health" });

    expect(result).toEqual({ status: "ok" });
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:3000/api/health", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "X-Session-Token": "token-123",
      },
      body: undefined,
      signal: undefined,
    });
  });

  it("lève une ApiError sur code HTTP >=400", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Not allowed" }), {
        status: 403,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const client = new ApiClient();
    await expect(client.request({ path: "/projects" })).rejects.toBeInstanceOf(ApiError);
  });
});
