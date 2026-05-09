/**
 * Generated from packages/contracts/openapi/openapi.json.
 *
 * Orval is the configured generator for this package. This deterministic
 * fallback was produced from the committed FastAPI OpenAPI artifact because
 * package-manager execution is blocked in the current sandbox.
 */

export type DependencyHealthStatus =
  | "ok"
  | "configured"
  | "unavailable"
  | "not_configured";

export interface DependencyHealth {
  detail?: string | null;
  name: string;
  status: DependencyHealthStatus;
}

export interface HealthResponse {
  api_version: string;
  dependencies: DependencyHealth[];
  runtime_mode: string;
  status: "ok";
}

export interface HealthHealthGetRequestConfig {
  baseUrl?: string;
  fetch?: typeof fetch;
  headers?: HeadersInit;
  signal?: AbortSignal;
}

export const getHealthHealthGetUrl = () => "/health";

export const getHealthHealthGetQueryKey = () => [getHealthHealthGetUrl()] as const;

export type HealthHealthGetQueryKey = ReturnType<typeof getHealthHealthGetQueryKey>;

export async function healthHealthGet(
  config: HealthHealthGetRequestConfig = {},
): Promise<HealthResponse> {
  const fetcher = config.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the health client.");
  }

  const baseUrl = config.baseUrl ?? "";
  const response = await fetcher(`${baseUrl}${getHealthHealthGetUrl()}`, {
    headers: config.headers,
    method: "GET",
    signal: config.signal,
  });

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`);
  }

  return (await response.json()) as HealthResponse;
}

export type HealthHealthGetResult = Awaited<ReturnType<typeof healthHealthGet>>;
