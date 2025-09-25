export interface RequestOptions<TBody = unknown> {
  path: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: TBody;
  signal?: AbortSignal;
}

export interface ApiClientConfig {
  baseUrl?: string;
  getSessionToken?: () => string | null | undefined;
}

export class ApiError extends Error {
  public readonly status: number;
  public readonly details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly getSessionToken?: () => string | null | undefined;

  constructor({ baseUrl, getSessionToken }: ApiClientConfig = {}) {
    const fallbackBase = import.meta.env.VITE_API_BASE_URL ?? "/api";
    const resolvedBase = baseUrl ?? fallbackBase;
    const defaultOrigin =
      typeof window !== "undefined" ? window.location.origin : "http://localhost";
    const normalizedBase = resolvedBase.startsWith("http")
      ? resolvedBase
      : resolvedBase.startsWith("/")
        ? `${defaultOrigin}${resolvedBase}`
        : resolvedBase;
    this.baseUrl = normalizedBase.replace(/\/+$/, "");
    this.getSessionToken = getSessionToken;
  }

  async request<TResponse, TBody = unknown>({
    path,
    method = "GET",
    body,
    signal,
  }: RequestOptions<TBody>): Promise<TResponse> {
    const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
    const url = new URL(normalizedPath, `${this.baseUrl}/`);
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const sessionToken = this.getSessionToken?.();
    if (sessionToken) {
      headers["X-Session-Token"] = sessionToken;
    }

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal,
    });

    const text = await response.text();
    const data = text ? JSON.parse(text) : null;

    if (!response.ok) {
      throw new ApiError(
        data?.detail ?? response.statusText ?? "Request failed",
        response.status,
        data,
      );
    }

    return data as TResponse;
  }
}
