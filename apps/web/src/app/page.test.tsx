import "@/test/setup";

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  getHealthHealthGetUrl,
  type HealthResponse,
} from "@caragent/contracts";

import {
  mapHealthResponse,
  type FoundationStatusCard,
} from "@/lib/api/health";

import Home from "./page";

const healthFixture: HealthResponse = {
  api_version: "0.1.0",
  dependencies: [
    { name: "database", status: "ok" },
    { name: "redis", status: "ok" },
    { name: "object_storage", status: "ok" },
    { detail: "Worker 将在后续任务接入队列状态", name: "worker", status: "not_configured" },
    { name: "contracts", status: "ok" },
  ],
  runtime_mode: "local",
  status: "ok",
};

const configuredHealthFixture: HealthResponse = {
  api_version: "0.1.0",
  dependencies: [
    {
      detail: "Dependency is configured; live validation is performed by pnpm smoke:local.",
      name: "database",
      status: "configured",
    },
    {
      detail: "Dependency is configured; live validation is performed by pnpm smoke:local.",
      name: "redis",
      status: "configured",
    },
    {
      detail: "Dependency is configured; live validation is performed by pnpm smoke:local.",
      name: "object_storage",
      status: "configured",
    },
    { detail: "Worker 将在后续任务接入队列状态", name: "worker", status: "not_configured" },
    { name: "contracts", status: "ok" },
  ],
  runtime_mode: "local",
  status: "ok",
};

describe("Phase 1 foundation shell", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the approved shell copy and five foundation cards", () => {
    render(<Home />);

    for (const copy of ["痛车设计 Agent", "检查堆栈健康", "工作台基础已就绪"]) {
      expect(screen.getByText(copy)).toBeVisible();
    }

    for (const cardLabel of ["Web", "API", "Worker", "Contracts", "Local Services"]) {
      expect(screen.getByText(cardLabel)).toBeVisible();
    }
  });

  it("keeps future workbench regions disabled with accessible explanatory copy", () => {
    render(<Home />);

    for (const region of ["对话", "参数", "素材", "预览", "历史", "生成", "导出", "3D"]) {
      const item = screen.getByRole("button", {
        name: new RegExp(`${region}.*后续阶段开放`),
      });

      expect(item).toBeDisabled();
      expect(item).toHaveAttribute("aria-disabled", "true");
      expect(item).toHaveAttribute("title", "后续阶段开放");
    }

    expect(screen.getAllByText("后续阶段开放").length).toBeGreaterThanOrEqual(8);
  });

  it("does not expose deferred product controls", () => {
    render(<Home />);

    const forbiddenButtonNames = [
      "输入提示词",
      "上传素材",
      "开始生成",
      "导出图片",
      "画布控制",
      "prompt input",
      "up" + "load button",
      "gen" + "erate button",
      "ex" + "port button",
      "can" + "vas controls",
    ];

    for (const label of forbiddenButtonNames) {
      expect(
        screen.queryByRole("button", { name: new RegExp(label, "i") }),
      ).not.toBeInTheDocument();
    }

    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("shows the loading state while checking stack health", async () => {
    const user = userEvent.setup();
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => {})));
    render(<Home />);

    await user.click(screen.getByRole("button", { name: "检查堆栈健康" }));

    expect(screen.getByRole("button", { name: "检查堆栈健康" })).toHaveTextContent(
      "正在检查服务...",
    );
  });

  it("calls the contract health URL and updates shell state", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(healthFixture), {
        headers: { "content-type": "application/json" },
        status: 200,
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<Home />);

    await user.click(screen.getByRole("button", { name: "检查堆栈健康" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        `http://localhost:8000${getHealthHealthGetUrl()}`,
        expect.objectContaining({ method: "GET" }),
      );
    });
    expect(await screen.findByText("API 健康检查通过 (0.1.0)")).toBeVisible();
  });

  it("shows configured local services without claiming live health success", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(configuredHealthFixture), {
        headers: { "content-type": "application/json" },
        status: 200,
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<Home />);

    await user.click(screen.getByRole("button", { name: "检查堆栈健康" }));

    expect(
      await screen.findByText(
        "PostgreSQL、Redis 和 MinIO 已配置；运行 pnpm smoke:local 验证本地服务。",
      ),
    ).toBeVisible();
    expect(screen.getByText("已配置")).toBeVisible();
    expect(
      screen.queryByText("PostgreSQL、Redis 和 MinIO 健康检查通过。"),
    ).not.toBeInTheDocument();
  });

  it("maps the contract health response into the five shell status cards", () => {
    const result = mapHealthResponse(healthFixture, "http://api.test");
    const cardsByLabel = new Map(
      result.cards.map((card: FoundationStatusCard) => [card.label, card]),
    );

    expect(result.apiBaseUrl).toBe("http://api.test");
    expect(result.runtimeMode).toBe("local");
    expect(result.contractStatus).toBe("current");
    expect([...cardsByLabel.keys()]).toEqual([
      "Web",
      "API",
      "Worker",
      "Contracts",
      "Local Services",
    ]);
    expect(cardsByLabel.get("Contracts")?.statusLabel).toBe("已生成");
    expect(cardsByLabel.get("Local Services")?.statusLabel).toBe("已连接");
  });

  it("maps configured local services to a non-connected configured state", () => {
    const result = mapHealthResponse(configuredHealthFixture, "http://api.test");
    const localServices = result.cards.find((card) => card.id === "local-services");

    expect(localServices?.state).toBe("configured");
    expect(localServices?.statusLabel).toBe("已配置");
    expect(localServices?.detail).toBe(
      "PostgreSQL、Redis 和 MinIO 已配置；运行 pnpm smoke:local 验证本地服务。",
    );
  });
});
