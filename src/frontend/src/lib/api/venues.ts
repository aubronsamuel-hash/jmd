import { ApiClient } from "./client";
import type { Venue } from "./types";

export function createVenuesApi(client: ApiClient) {
  return {
    list: () => client.request<Venue[]>({ path: "/venues" }),
  };
}
