import {
  healthHealthGet,
  type DependencyHealth,
  type HealthResponse,
} from "@caragent/contracts";

import { publicEnv } from "@/lib/config/public-env";

export type FoundationStatusId =
  | "web"
  | "api"
  | "worker"
  | "contracts"
  | "local-services";

export type FoundationStatusState =
  | "connected"
  | "generated"
  | "unavailable"
  | "not-configured";

export interface FoundationStatusCard {
  detail: string;
  id: FoundationStatusId;
  label: "Web" | "API" | "Worker" | "Contracts" | "Local Services";
  state: FoundationStatusState;
  statusLabel: string;
}

export interface StackHealthResult {
  apiBaseUrl: string;
  apiVersion: string;
  cards: FoundationStatusCard[];
  contractStatus: "current" | "stale";
  runtimeMode: string;
}

export interface CheckStackHealthOptions {
  apiBaseUrl?: string;
  fetch?: typeof fetch;
  signal?: AbortSignal;
}

const serviceDependencyNames = ["database", "redis", "object_storage"] as const;

export async function checkStackHealth(
  options: CheckStackHealthOptions = {},
): Promise<StackHealthResult> {
  const apiBaseUrl = options.apiBaseUrl ?? publicEnv.apiBaseUrl;
  const response = await healthHealthGet({
    baseUrl: apiBaseUrl,
    fetch: options.fetch,
    signal: options.signal,
  });

  return mapHealthResponse(response, apiBaseUrl);
}

export function mapHealthResponse(
  response: HealthResponse,
  apiBaseUrl = publicEnv.apiBaseUrl,
): StackHealthResult {
  const dependencies = new Map(
    response.dependencies.map((dependency) => [
      normalizeDependencyName(dependency.name),
      dependency,
    ]),
  );
  const worker = dependencies.get("worker");
  const contracts = dependencies.get("contracts");
  const localServices = serviceDependencyNames
    .map((name) => dependencies.get(name))
    .filter((dependency): dependency is DependencyHealth => Boolean(dependency));

  return {
    apiBaseUrl,
    apiVersion: response.api_version,
    cards: [
      {
        detail: "Next.js workbench shell is loaded.",
        id: "web",
        label: "Web",
        state: "connected",
        statusLabel: "已连接",
      },
      {
        detail: `API 健康检查通过 (${response.api_version})`,
        id: "api",
        label: "API",
        state: "connected",
        statusLabel: "已连接",
      },
      dependencyCard("worker", "Worker", worker, "Worker 将在后续任务接入队列状态"),
      dependencyCard("contracts", "Contracts", contracts, "API 合约需要重新生成"),
      localServicesCard(localServices),
    ],
    contractStatus: contracts?.status === "ok" ? "current" : "stale",
    runtimeMode: response.runtime_mode,
  };
}

function dependencyCard(
  id: FoundationStatusId,
  label: FoundationStatusCard["label"],
  dependency: DependencyHealth | undefined,
  fallbackDetail: string,
): FoundationStatusCard {
  if (!dependency) {
    return {
      detail: fallbackDetail,
      id,
      label,
      state: "unavailable",
      statusLabel: label === "Contracts" ? "需要重新生成" : "未连接",
    };
  }

  if (dependency.status === "ok") {
    return {
      detail: dependency.detail ?? `${label} ready.`,
      id,
      label,
      state: label === "Contracts" ? "generated" : "connected",
      statusLabel: label === "Contracts" ? "已生成" : "已连接",
    };
  }

  if (dependency.status === "not_configured") {
    return {
      detail: dependency.detail ?? fallbackDetail,
      id,
      label,
      state: "not-configured",
      statusLabel: "未配置",
    };
  }

  return {
    detail: dependency.detail ?? fallbackDetail,
    id,
    label,
    state: "unavailable",
    statusLabel: label === "Contracts" ? "需要重新生成" : "未连接",
  };
}

function localServicesCard(
  dependencies: DependencyHealth[],
): FoundationStatusCard {
  if (dependencies.length === 0) {
    return {
      detail: "PostgreSQL、Redis 和 MinIO 状态尚未返回。",
      id: "local-services",
      label: "Local Services",
      state: "unavailable",
      statusLabel: "未连接",
    };
  }

  if (dependencies.every((dependency) => dependency.status === "ok")) {
    return {
      detail: "PostgreSQL、Redis 和 MinIO 健康检查通过。",
      id: "local-services",
      label: "Local Services",
      state: "connected",
      statusLabel: "已连接",
    };
  }

  if (dependencies.some((dependency) => dependency.status === "unavailable")) {
    return {
      detail: dependencies
        .filter((dependency) => dependency.status === "unavailable")
        .map((dependency) => dependency.detail ?? dependency.name)
        .join("；"),
      id: "local-services",
      label: "Local Services",
      state: "unavailable",
      statusLabel: "未连接",
    };
  }

  return {
    detail: "本地基础服务需要启动后才能完成健康检查。",
    id: "local-services",
    label: "Local Services",
    state: "not-configured",
    statusLabel: "未配置",
  };
}

function normalizeDependencyName(name: string) {
  return name.trim().toLowerCase().replaceAll("-", "_");
}
