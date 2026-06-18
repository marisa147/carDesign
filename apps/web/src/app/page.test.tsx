import "@/test/setup";

import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getListAssetsWorkspacesWorkspaceIdAssetsGetUrl,
  getCreateGenerationBriefRouteWorkspacesWorkspaceIdGenerationBriefsPostUrl,
  getCreateMessageWorkspacesWorkspaceIdMessagesPostUrl,
  getCreateWorkspaceWorkspacesPostUrl,
  getGetJobJobsJobIdGetUrl,
  getGetWorkspaceWorkspacesWorkspaceIdGetUrl,
  getListArtifactsWorkspacesWorkspaceIdArtifactsGetUrl,
  getListDesignBriefsWorkspacesWorkspaceIdBriefsGetUrl,
  getListEventsJobsJobIdEventsGetUrl,
  getListExportsWorkspacesWorkspaceIdExportsGetUrl,
  getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl,
  getListJobsWorkspacesWorkspaceIdJobsGetUrl,
  getListMessagesWorkspacesWorkspaceIdMessagesGetUrl,
  getListVersionsWorkspacesWorkspaceIdVersionsGetUrl,
  getCancelJobJobsJobIdCancelPostUrl,
  getProviderStatusOperationsProviderStatusGetUrl,
  getRetryGenerationJobJobsJobIdRetryPostUrl,
  getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl,
  getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl,
  getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl,
  getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl,
  getUpdateAssetRightsAssetsAssetIdRightsPatchUrl,
  getUpdateGenerationBriefRouteGenerationBriefsBriefIdPatchUrl,
  getUploadAssetWorkspacesWorkspaceIdAssetsPostUrl,
  type ArtifactResponse,
  type AssetResponse,
  type DesignBriefResponse,
  type DesignVersionResponse,
  type ExportResponse,
  type FeedbackResponse,
  type GenerationBriefResponse,
  type GenerationJobCancelResponse,
  type GenerationJobResponse,
  type GenerationJobSubmissionResponse,
  type JobEventResponse,
  type MessageResponse,
  type OperationsProviderStatusResponse,
  type WorkspaceResponse,
} from "@caragent/contracts";

import { useWorkbenchStore } from "@/lib/workbench/store";

import Home from "./page";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status,
  });
}

const createdAt = "2026-06-17T00:00:00Z";

const workspaceFixture: WorkspaceResponse = {
  created_at: createdAt,
  id: "workspace-1",
  owner_id: null,
  status: "active",
  title: "痛车设计工作台",
  updated_at: createdAt,
};

const messageFixture: MessageResponse = {
  content: "白色双门车，樱色女主角，车门文字 MOON DRIVE。",
  created_at: createdAt,
  id: "message-1",
  role: "user",
  sequence: 1,
  updated_at: createdAt,
  workspace_id: "workspace-1",
};

const previewSpecFixture = {
  canvas: { height: 768, width: 1536 },
  overlay_layers: [
    { id: "text-1", kind: "text", text: "MOON DRIVE", zone_id: "door-main" },
    { asset_id: "logo-1", id: "logo-1", kind: "logo", zone_id: "rear-quarter" },
  ],
  safe_zones: [
    {
      height: 0.24,
      id: "door-main",
      kind: "body",
      label: "Door / main side panel",
      width: 0.34,
      x: 0.32,
      y: 0.47,
    },
    {
      height: 0.2,
      id: "rear-quarter",
      kind: "body",
      label: "Rear quarter panel",
      width: 0.18,
      x: 0.64,
      y: 0.43,
    },
  ],
  sources: {
    overlay_logo_asset_ids: ["logo-1"],
    reference_asset_ids: [],
  },
  template: {
    id: "generic-side-coupe",
    label: "Generic side-view coupe",
    view: "side",
  },
  warnings: [{ id: "warning-1", message: "Text may be hard to read." }],
};

const briefFixture: GenerationBriefResponse = {
  created_at: createdAt,
  id: "brief-1",
  payload: {
    canvas_height: 768,
    canvas_width: 1536,
    character_focus: "车门大角色，后翼子板小表情",
    character_theme: "樱色女主角",
    color_harmony: "白底、青绿色点缀、银色分隔线",
    coverage: "balanced side coverage",
    original_request: "白色双门车，樱色女主角，车门文字 MOON DRIVE。",
    overlay_logo_asset_ids: [],
    palette: ["white", "teal"],
    racing_cues: ["号码牌", "拖车箭头"],
    reference_asset_ids: [],
    safe_zones: previewSpecFixture.safe_zones,
    style: "清爽赛博风",
    supporting_graphics: ["樱花瓣", "青绿色丝带"],
    text: ["MOON DRIVE"],
    typography_intent: "车门大字，保持可读",
    vehicle_template_id: "generic-side-coupe",
    vehicle_template_label: "Generic side-view coupe",
    view: "side",
    warnings: ["Text may be hard to read."],
  },
  source_message_id: "message-1",
  status: "draft",
  title: "Workbench brief",
  updated_at: createdAt,
  workspace_id: "workspace-1",
};

const designBriefFixture: DesignBriefResponse = {
  ...briefFixture,
  payload: { ...briefFixture.payload },
};

const updatedBriefFixture: GenerationBriefResponse = {
  ...briefFixture,
  payload: {
    ...briefFixture.payload,
    palette: ["white", "magenta"],
    style: "霓虹赛博风",
    text: ["MOON DRIVE", "SAKURA MODE"],
  },
  updated_at: "2026-06-17T00:05:00Z",
};

const phase6UpdatedBriefFixture: GenerationBriefResponse = {
  ...briefFixture,
  payload: {
    ...briefFixture.payload,
    character_focus: "后翼子板 chibi，车门保留大标题",
    color_harmony: "青绿色主导，白色留白",
    overlay_logo_asset_ids: ["logo-1"],
    racing_cues: ["侧裙速度线"],
    supporting_graphics: ["速度线", "星形贴纸"],
    typography_intent: "堆叠式粗体",
  },
  updated_at: "2026-06-17T00:08:00Z",
};

const missingRightsAssetFixture: AssetResponse = {
  byte_size: 128,
  checksum_sha256: "c".repeat(64),
  content_type: "image/png",
  created_at: createdAt,
  id: "asset-1",
  kind: "reference",
  object_key: "workspaces/workspace-1/uploads/asset-1/reference.png",
  original_filename: "reference.png",
  rights_confirmed_at: null,
  rights_notes: null,
  rights_status: "missing",
  source_label: null,
  source_url: null,
  thumbnail_object_key: null,
  updated_at: createdAt,
  workspace_id: "workspace-1",
};

const confirmedAssetFixture: AssetResponse = {
  ...missingRightsAssetFixture,
  rights_confirmed_at: "2026-06-17T00:10:00Z",
  rights_notes: "用户自有素材",
  rights_status: "confirmed",
  source_label: "原创上传",
  updated_at: "2026-06-17T00:10:00Z",
};

const confirmedCharacterAssetFixture: AssetResponse = {
  ...confirmedAssetFixture,
  id: "asset-2",
  object_key: "workspaces/workspace-1/uploads/asset-2/confirmed-reference.png",
  original_filename: "confirmed-reference.png",
};

const referenceBriefFixture: GenerationBriefResponse = {
  ...updatedBriefFixture,
  payload: {
    ...updatedBriefFixture.payload,
    reference_asset_ids: ["asset-1"],
  },
  updated_at: "2026-06-17T00:12:00Z",
};

const generationJobFixture: GenerationJobResponse = {
  actual_cost: null,
  brief_id: "brief-1",
  created_at: createdAt,
  estimated_cost: null,
  id: "job-1",
  idempotency_key: "phase4-generation",
  latest_error: null,
  model: null,
  operation: "generate_2d_concept",
  provider: null,
  requested_by: "web-workbench",
  status: "queued",
  updated_at: createdAt,
  workspace_id: "workspace-1",
};

const failedJobFixture: GenerationJobResponse = {
  ...generationJobFixture,
  latest_error: "Provider timeout",
  status: "failed",
  updated_at: "2026-06-17T00:20:00Z",
};

const jobEventFixture: JobEventResponse = {
  created_at: createdAt,
  event_type: "created",
  id: "event-1",
  job_id: "job-1",
  message: "Job queued.",
  progress: null,
  sequence: 1,
  source: "api",
  status: "queued",
  updated_at: createdAt,
};

const operationsStatusFixture: OperationsProviderStatusResponse = {
  api_version: "0.1.0",
  provider: {
    active_mode: "local-deterministic",
    bfl_key_configured: false,
    capabilities: [
      {
        blocked_reasons: [],
        credential_configured: true,
        credential_required: false,
        default_model: "local-concept-v1",
        display_name: "Local deterministic",
        enabled: true,
        estimated_cost: null,
        provider: "local-deterministic",
      },
      {
        blocked_reasons: [
          "AI_PROVIDER_CALLS_ENABLED is disabled",
          "AI_PROVIDER_BFL_API_KEY is missing",
        ],
        credential_configured: false,
        credential_required: true,
        default_model: "flux-2-pro-preview",
        display_name: "BFL",
        enabled: false,
        estimated_cost: { max_per_job: null },
        provider: "bfl",
      },
    ],
    calls_enabled: false,
    default_provider: "disabled",
    guard_state: {
      daily_call_limit: null,
      hosted_quota_guard_enabled: false,
      max_estimated_cost_per_job: null,
      rate_limit_per_minute: null,
    },
    hosted_calls_blocked_reason: null,
    hosted_daily_call_limit: null,
    hosted_provider_configured: false,
    hosted_quota_guard_enabled: false,
    hosted_rate_limit_per_minute: null,
    max_estimated_cost_per_job: null,
    supported_providers: ["local-deterministic", "bfl"],
  },
  queue: {
    active_tasks: 0,
    active_workers: 0,
    detail: "No worker replied.",
    generation_queue: "caragent.default",
    registered_tasks: [],
    reserved_tasks: 0,
    status: "unavailable",
  },
  recent_failures: [],
  runtime_mode: "local",
  worker: {
    active_workers: 0,
    detail: "No worker replied.",
    status: "unavailable",
    task_name: "caragent_worker.generate_2d_concept_job",
  },
};

const guardedHostedOperationsStatusFixture: OperationsProviderStatusResponse = {
  ...operationsStatusFixture,
  provider: {
    active_mode: "bfl",
    bfl_key_configured: true,
    capabilities: [
      operationsStatusFixture.provider.capabilities?.[0] ?? {},
      {
        blocked_reasons: [],
        credential_configured: true,
        credential_required: true,
        default_model: "flux-2-pro-preview",
        display_name: "BFL",
        enabled: true,
        estimated_cost: { max_per_job: "0.7500" },
        provider: "bfl",
      },
    ],
    calls_enabled: true,
    default_provider: "bfl",
    guard_state: {
      daily_call_limit: 25,
      hosted_quota_guard_enabled: true,
      max_estimated_cost_per_job: "0.7500",
      rate_limit_per_minute: 4,
    },
    hosted_calls_blocked_reason: null,
    hosted_daily_call_limit: 25,
    hosted_provider_configured: true,
    hosted_quota_guard_enabled: true,
    hosted_rate_limit_per_minute: 4,
    max_estimated_cost_per_job: "0.7500",
    supported_providers: ["local-deterministic", "bfl"],
  },
  queue: {
    ...operationsStatusFixture.queue,
    active_workers: 1,
    registered_tasks: ["caragent_worker.generate_2d_concept_job"],
    status: "ok",
  },
  worker: {
    ...operationsStatusFixture.worker,
    active_workers: 1,
    status: "ok",
  },
};

const artifactFixture: ArtifactResponse = {
  asset_id: null,
  byte_size: 512,
  checksum_sha256: "d".repeat(64),
  content_type: "image/png",
  created_at: createdAt,
  height: 768,
  id: "artifact-1",
  job_id: "job-1",
  kind: "generated_image",
  object_key: "workspaces/workspace-1/generated_image/artifact-1/concept.png",
  updated_at: createdAt,
  version_id: "version-1",
  width: 1536,
  workspace_id: "workspace-1",
};

const secondArtifactFixture: ArtifactResponse = {
  ...artifactFixture,
  id: "artifact-2",
  object_key: "workspaces/workspace-1/generated_image/artifact-2/concept-alt.png",
  updated_at: "2026-06-17T00:25:00Z",
  version_id: "version-2",
};

const versionFixture: DesignVersionResponse = {
  brief_id: "brief-1",
  created_at: createdAt,
  id: "version-1",
  job_id: "job-1",
  lineage_depth: 0,
  parameters: {
    concept_label: "concept_preview",
    coverage: "balanced side coverage",
    overlay_layer_count: 2,
    palette: ["white", "teal"],
    preview_spec: previewSpecFixture,
    safe_zone_count: 2,
    warning_count: 1,
  },
  parent_version_id: null,
  status: "generated",
  summary: "Generated 2D concept preview.",
  title: "版本 1",
  updated_at: createdAt,
  workspace_id: "workspace-1",
};

const secondVersionFixture: DesignVersionResponse = {
  ...versionFixture,
  id: "version-2",
  lineage_depth: 1,
  parameters: {
    concept_label: "concept_preview",
    coverage: "door focus",
    palette: ["white", "pink"],
  },
  parent_version_id: "version-1",
  summary: "Second 2D concept preview.",
  title: "版本 2",
  updated_at: "2026-06-17T00:25:00Z",
};

const feedbackFixture: FeedbackResponse = {
  approval_state: "approved",
  comment: "这个方向可以继续。",
  created_at: "2026-06-17T00:40:00Z",
  id: "feedback-1",
  rating: 5,
  updated_at: "2026-06-17T00:40:00Z",
  version_id: "version-2",
  workspace_id: "workspace-1",
};

const targetedRecompositionVersionFixture: DesignVersionResponse = {
  ...versionFixture,
  id: "version-targeted-recomposition",
  lineage_depth: 1,
  parameters: {
    changed_fields: ["text", "y"],
    edit_route: "deterministic_recomposition",
    mask_artifact_id: "artifact-1",
    prompt_delta: {
      instructions: ["把门板文字上移"],
      summary: "把门板文字上移",
    },
    region: {
      height: 0.24,
      type: "rectangle",
      unit: "normalized",
      width: 0.34,
      x: 0.32,
      y: 0.47,
    },
    target: {
      id: "text-1",
      type: "overlay_layer",
    },
  },
  parent_version_id: "version-1",
  summary: "Text layer moved within the door area.",
  title: "局部编辑 1",
  updated_at: "2026-06-17T00:35:00Z",
};

const targetedProviderVersionFixture: DesignVersionResponse = {
  ...targetedRecompositionVersionFixture,
  id: "version-targeted-provider",
  parameters: {
    edit_route: "provider_masked_generation",
    estimated_cost: "0.6500",
    mask_artifact_id: "artifact-1",
    model: "flux-2-pro-preview",
    prompt_delta: {
      instructions: ["重绘后翼子板角色表情"],
      summary: "重绘后翼子板角色表情",
    },
    provider: "bfl",
    region: {
      height: 0.2,
      type: "rectangle",
      unit: "normalized",
      width: 0.18,
      x: 0.64,
      y: 0.43,
    },
    target: {
      id: "rear-quarter",
      type: "safe_zone",
    },
  },
  summary: "Provider masked edit for rear quarter.",
  title: "托管局部编辑",
  updated_at: "2026-06-17T00:38:00Z",
};

const orphanTargetedVersionFixture: DesignVersionResponse = {
  ...targetedRecompositionVersionFixture,
  id: "version-targeted-orphan",
  parent_version_id: "missing-parent",
  title: "孤立局部编辑",
};

const exportFixture: ExportResponse = {
  artifact_id: "artifact-2",
  completed_at: null,
  concept_label: "client-review",
  created_at: "2026-06-17T00:42:00Z",
  format: "png",
  id: "export-1",
  manifest: {
    disclaimer: "Concept preview only, not print-ready.",
    parameters: {
      concept_label: "concept_preview",
      preview_spec: previewSpecFixture,
    },
    source_artifact_object_key: secondArtifactFixture.object_key,
    version_id: "version-2",
  },
  requested_at: "2026-06-17T00:42:00Z",
  status: "requested",
  updated_at: "2026-06-17T00:42:00Z",
  version_id: "version-2",
  workspace_id: "workspace-1",
};

function mockResumeWithGenerationState({
  artifacts = [],
  events = [jobEventFixture],
  exports = [],
  feedback = [],
  job = generationJobFixture,
  versions = [],
}: {
  artifacts?: ArtifactResponse[];
  events?: JobEventResponse[];
  exports?: ExportResponse[];
  feedback?: FeedbackResponse[];
  job?: GenerationJobResponse;
  versions?: DesignVersionResponse[];
}) {
  return vi
    .fn()
    .mockResolvedValueOnce(jsonResponse(workspaceFixture))
    .mockResolvedValueOnce(jsonResponse([messageFixture]))
    .mockResolvedValueOnce(jsonResponse([designBriefFixture]))
    .mockResolvedValueOnce(jsonResponse([]))
    .mockResolvedValueOnce(jsonResponse([job]))
    .mockResolvedValueOnce(jsonResponse(job))
    .mockResolvedValueOnce(jsonResponse(events))
    .mockResolvedValueOnce(jsonResponse(artifacts))
    .mockResolvedValueOnce(jsonResponse(versions))
    .mockResolvedValueOnce(jsonResponse(feedback))
    .mockResolvedValueOnce(jsonResponse(exports));
}

describe("Phase 4 workbench shell", () => {
  afterEach(() => {
    act(() => {
      useWorkbenchStore.getState().resetWorkbenchUi();
    });
    localStorage.clear();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the integrated workbench regions as the first screen", () => {
    render(<Home />);

    for (const copy of [
      "痛车设计 Agent",
      "对话",
      "2D 预览",
      "参数",
      "素材",
      "进度",
      "历史方案",
    ]) {
      expect(screen.getByText(copy)).toBeVisible();
    }

    expect(screen.getByRole("textbox", { name: "设计需求" })).toBeVisible();
    expect(screen.getByRole("button", { name: "发送需求" })).toBeDisabled();
  });

  it("shows future capabilities as disabled or deferred gates", () => {
    render(<Home />);

    for (const name of [
      "3D 预览后续开放",
      "生产导出后续开放",
      "市场功能后续开放",
    ]) {
      const gate = screen.getByRole("button", { name });
      expect(gate).toBeDisabled();
      expect(gate).toHaveAttribute("aria-disabled", "true");
    }
  });

  it("does not present Phase 1-3 proof panels as the primary experience", () => {
    render(<Home />);

    expect(screen.queryByText("工作台基础已就绪")).not.toBeInTheDocument();
    expect(screen.queryByText("Phase 2 持久状态")).not.toBeInTheDocument();
    expect(screen.queryByText("Phase 3 概念生成证明")).not.toBeInTheDocument();
  });

  it("keeps compact local runtime status visible", () => {
    render(<Home />);

    expect(screen.getByText("local")).toBeVisible();
    expect(screen.getByText(/API base URL:/)).toBeVisible();
    expect(screen.getByText("API 合约已生成")).toBeVisible();
  });

  it("creates a workspace, durable message, and structured brief from chat submit", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture, 201))
      .mockResolvedValueOnce(jsonResponse(messageFixture, 201))
      .mockResolvedValueOnce(jsonResponse(briefFixture, 201));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    await user.type(
      screen.getByRole("textbox", { name: "设计需求" }),
      "白色双门车，樱色女主角，车门文字 MOON DRIVE。",
    );
    await user.click(screen.getByRole("button", { name: "发送需求" }));

    expect(await screen.findByText(messageFixture.content)).toBeVisible();
    expect(screen.getByText("结构化 brief 已保存")).toBeVisible();
    expect(localStorage.getItem("caragent.workbench.workspaceId")).toBe(
      "workspace-1",
    );
    expect(localStorage.getItem("caragent.workbench.briefId")).toBe("brief-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      `http://localhost:8000${getCreateWorkspaceWorkspacesPostUrl()}`,
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://localhost:8000${getCreateMessageWorkspacesWorkspaceIdMessagesPostUrl("workspace-1")}`,
      expect.objectContaining({
        body: JSON.stringify({
          content: messageFixture.content,
          role: "user",
        }),
        method: "POST",
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      `http://localhost:8000${getCreateGenerationBriefRouteWorkspacesWorkspaceIdGenerationBriefsPostUrl("workspace-1")}`,
      expect.objectContaining({
        body: JSON.stringify({
          original_request: messageFixture.content,
          source_message_id: "message-1",
          title: "Workbench brief",
        }),
        method: "POST",
      }),
    );
    expect(
      fetchMock.mock.calls.some(
        ([url]) =>
          url ===
          `http://localhost:8000${getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl("workspace-1")}`,
      ),
    ).toBe(false);
  });

  it("refetches durable chat and brief state after remount", async () => {
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture))
      .mockResolvedValueOnce(jsonResponse([messageFixture]))
      .mockResolvedValueOnce(jsonResponse([designBriefFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText(messageFixture.content)).toBeVisible();
    expect(screen.getByText("结构化 brief 已保存")).toBeVisible();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getGetWorkspaceWorkspacesWorkspaceIdGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListMessagesWorkspacesWorkspaceIdMessagesGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListDesignBriefsWorkspacesWorkspaceIdBriefsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListAssetsWorkspacesWorkspaceIdAssetsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListJobsWorkspacesWorkspaceIdJobsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("shows an empty parameter state before a brief exists", () => {
    render(<Home />);

    expect(screen.getByText("等待 brief")).toBeVisible();
    expect(
      screen.getByText("先发送设计需求以生成结构化 brief。"),
    ).toBeVisible();
    expect(screen.getByRole("button", { name: "保存参数" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "提交反馈" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "创建概念导出" })).toBeDisabled();
  });

  it("edits structured brief parameters without submitting generation", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture))
      .mockResolvedValueOnce(jsonResponse([messageFixture]))
      .mockResolvedValueOnce(jsonResponse([designBriefFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(updatedBriefFixture));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByDisplayValue("清爽赛博风")).toBeVisible();
    expect(screen.getByText("Generic side-view coupe")).toBeVisible();
    expect(screen.getByText("side")).toBeVisible();
    expect(screen.getByDisplayValue("balanced side coverage")).toBeVisible();
    expect(screen.getByRole("textbox", { name: "配色" })).toHaveValue(
      "white\nteal",
    );
    expect(screen.getByRole("textbox", { name: "文案" })).toHaveValue("MOON DRIVE");

    await user.clear(screen.getByRole("textbox", { name: "风格" }));
    await user.type(screen.getByRole("textbox", { name: "风格" }), "霓虹赛博风");
    await user.clear(screen.getByRole("textbox", { name: "配色" }));
    await user.type(screen.getByRole("textbox", { name: "配色" }), "white\nmagenta");
    await user.clear(screen.getByRole("textbox", { name: "文案" }));
    await user.type(
      screen.getByRole("textbox", { name: "文案" }),
      "MOON DRIVE\nSAKURA MODE",
    );
    await user.click(screen.getByRole("button", { name: "保存参数" }));

    expect(await screen.findByText("参数已保存")).toBeVisible();
    expect(screen.getByDisplayValue("霓虹赛博风")).toBeVisible();
    expect(screen.getByRole("textbox", { name: "配色" })).toHaveValue(
      "white\nmagenta",
    );
    expect(screen.getByRole("textbox", { name: "文案" })).toHaveValue(
      "MOON DRIVE\nSAKURA MODE",
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      `http://localhost:8000${getUpdateGenerationBriefRouteGenerationBriefsBriefIdPatchUrl("brief-1")}`,
      expect.objectContaining({
        method: "PATCH",
      }),
    );
    const patchInit = fetchMock.mock.calls[5]?.[1] as RequestInit;
    expect(JSON.parse(String(patchInit.body))).toEqual({
      palette: ["white", "magenta"],
      style: "霓虹赛博风",
      text: ["MOON DRIVE", "SAKURA MODE"],
    });
    expect(
      fetchMock.mock.calls.some(
        ([url]) =>
          url ===
          `http://localhost:8000${getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl("workspace-1")}`,
      ),
    ).toBe(false);
  });

  it("edits Phase 6 itasha controls without submitting generation", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture))
      .mockResolvedValueOnce(jsonResponse([messageFixture]))
      .mockResolvedValueOnce(jsonResponse([designBriefFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(phase6UpdatedBriefFixture));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("痛车设计控制")).toBeVisible();
    expect(screen.getByRole("textbox", { name: "角色焦点" })).toHaveValue(
      "车门大角色，后翼子板小表情",
    );
    expect(screen.getByRole("textbox", { name: "辅助图形" })).toHaveValue(
      "樱花瓣\n青绿色丝带",
    );
    expect(screen.getByRole("textbox", { name: "赛车/JDM 元素" })).toHaveValue(
      "号码牌\n拖车箭头",
    );
    expect(screen.getByRole("textbox", { name: "字体意图" })).toHaveValue(
      "车门大字，保持可读",
    );
    expect(screen.getByRole("textbox", { name: "配色协调" })).toHaveValue(
      "白底、青绿色点缀、银色分隔线",
    );
    expect(screen.getByText("质量提示")).toBeVisible();
    expect(screen.getByText("Text may be hard to read.")).toBeVisible();

    await user.clear(screen.getByRole("textbox", { name: "角色焦点" }));
    await user.type(
      screen.getByRole("textbox", { name: "角色焦点" }),
      "后翼子板 chibi，车门保留大标题",
    );
    await user.clear(screen.getByRole("textbox", { name: "辅助图形" }));
    await user.type(screen.getByRole("textbox", { name: "辅助图形" }), "速度线\n星形贴纸");
    await user.clear(screen.getByRole("textbox", { name: "赛车/JDM 元素" }));
    await user.type(screen.getByRole("textbox", { name: "赛车/JDM 元素" }), "侧裙速度线");
    await user.clear(screen.getByRole("textbox", { name: "字体意图" }));
    await user.type(screen.getByRole("textbox", { name: "字体意图" }), "堆叠式粗体");
    await user.clear(screen.getByRole("textbox", { name: "配色协调" }));
    await user.type(screen.getByRole("textbox", { name: "配色协调" }), "青绿色主导，白色留白");
    await user.clear(screen.getByRole("textbox", { name: "文字/Logo 素材 ID" }));
    await user.type(screen.getByRole("textbox", { name: "文字/Logo 素材 ID" }), "logo-1");
    await user.click(screen.getByRole("button", { name: "保存参数" }));

    expect(await screen.findByText("参数已保存")).toBeVisible();
    const patchInit = fetchMock.mock.calls[5]?.[1] as RequestInit;
    expect(JSON.parse(String(patchInit.body))).toEqual({
      character_focus: "后翼子板 chibi，车门保留大标题",
      color_harmony: "青绿色主导，白色留白",
      overlay_logo_asset_ids: ["logo-1"],
      racing_cues: ["侧裙速度线"],
      supporting_graphics: ["速度线", "星形贴纸"],
      typography_intent: "堆叠式粗体",
    });
    expect(
      fetchMock.mock.calls.some(
        ([url]) =>
          url ===
          `http://localhost:8000${getSubmitGenerationJobWorkspacesWorkspaceIdGenerationJobsPostUrl("workspace-1")}`,
      ),
    ).toBe(false);
  });

  it("uploads assets, confirms rights, and saves confirmed references", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture))
      .mockResolvedValueOnce(jsonResponse([messageFixture]))
      .mockResolvedValueOnce(jsonResponse([designBriefFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(missingRightsAssetFixture, 201))
      .mockResolvedValueOnce(jsonResponse(confirmedAssetFixture))
      .mockResolvedValueOnce(jsonResponse(referenceBriefFixture));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    await screen.findByDisplayValue("清爽赛博风");
    const file = new File(["fake image"], "reference.png", { type: "image/png" });
    await user.upload(screen.getByLabelText("上传素材文件"), file);
    await user.click(screen.getByRole("button", { name: "上传素材" }));

    expect(await screen.findByText("reference.png")).toBeVisible();
    expect(screen.getByText("权利信息缺失")).toBeVisible();
    expect(
      screen.getByRole("checkbox", { name: "用于生成 reference.png" }),
    ).toBeDisabled();
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      `http://localhost:8000${getUploadAssetWorkspacesWorkspaceIdAssetsPostUrl("workspace-1")}`,
      expect.objectContaining({ method: "POST" }),
    );
    const uploadInit = fetchMock.mock.calls[5]?.[1] as RequestInit;
    expect(uploadInit.headers).toBeUndefined();
    expect(uploadInit.body).toBeInstanceOf(FormData);
    const uploadForm = uploadInit.body as FormData;
    expect(uploadForm.get("file")).toBe(file);
    expect(uploadForm.get("kind")).toBe("reference");

    await user.type(screen.getByLabelText("素材来源 reference.png"), "原创上传");
    await user.type(screen.getByLabelText("权利备注 reference.png"), "用户自有素材");
    await user.click(screen.getByRole("button", { name: "确认权利 reference.png" }));

    expect(await screen.findByText("权利已确认")).toBeVisible();
    const referenceCheckbox = screen.getByRole("checkbox", {
      name: "用于生成 reference.png",
    });
    expect(referenceCheckbox).toBeEnabled();
    expect(fetchMock).toHaveBeenNthCalledWith(
      7,
      `http://localhost:8000${getUpdateAssetRightsAssetsAssetIdRightsPatchUrl("asset-1")}`,
      expect.objectContaining({
        body: JSON.stringify({
          rights_notes: "用户自有素材",
          rights_status: "confirmed",
          source_label: "原创上传",
          source_url: null,
        }),
        method: "PATCH",
      }),
    );

    await user.click(referenceCheckbox);
    expect(screen.getByRole("textbox", { name: "引用素材 ID" })).toHaveValue("asset-1");
    await user.click(screen.getByRole("button", { name: "保存参数" }));

    expect(await screen.findByText("参数已保存")).toBeVisible();
    const patchInit = fetchMock.mock.calls[7]?.[1] as RequestInit;
    expect(JSON.parse(String(patchInit.body))).toEqual({
      reference_asset_ids: ["asset-1"],
      reference_usage: [
        {
          asset_id: "asset-1",
          enabled: true,
          role: "inspiration",
        },
      ],
    });
  });

  it("assigns reference roles, blocks missing-rights assets, and submits structured usage", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const structuredReferenceBrief = {
      ...briefFixture,
      payload: {
        ...briefFixture.payload,
        reference_asset_ids: ["asset-2"],
        reference_usage: [
          {
            asset_id: "asset-2",
            enabled: true,
            role: "style",
            schema_version: 1,
          },
        ],
      },
      updated_at: "2026-06-17T00:14:00Z",
    } satisfies GenerationBriefResponse;
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(workspaceFixture))
      .mockResolvedValueOnce(jsonResponse([messageFixture]))
      .mockResolvedValueOnce(jsonResponse([designBriefFixture]))
      .mockResolvedValueOnce(
        jsonResponse([missingRightsAssetFixture, confirmedCharacterAssetFixture]),
      )
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(structuredReferenceBrief));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("reference.png")).toBeVisible();
    expect(screen.getByText("confirmed-reference.png")).toBeVisible();
    for (const label of ["角色", "风格", "车辆", "Logo", "配色", "仅灵感"]) {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0);
    }
    expect(screen.getByText("需确认权利")).toBeVisible();
    expect(screen.getByText("引用素材需要权利确认")).toBeVisible();
    expect(
      screen.getByRole("checkbox", { name: "用于生成 reference.png" }),
    ).toBeDisabled();

    await user.selectOptions(
      screen.getByRole("combobox", { name: "引用角色 confirmed-reference.png" }),
      "style",
    );
    await user.click(
      screen.getByRole("checkbox", { name: "用于生成 confirmed-reference.png" }),
    );
    await user.click(screen.getByRole("button", { name: "保存参数" }));

    expect(await screen.findByText("参数已保存")).toBeVisible();
    const patchInit = fetchMock.mock.calls[5]?.[1] as RequestInit;
    expect(JSON.parse(String(patchInit.body))).toEqual({
      reference_asset_ids: ["asset-2"],
      reference_usage: [
        {
          asset_id: "asset-2",
          enabled: true,
          role: "style",
        },
      ],
    });
  });

  it.each([
    {
      event: { ...jobEventFixture, message: "Job queued.", status: "queued" },
      label: "排队中",
      status: "queued",
    },
    {
      event: {
        ...jobEventFixture,
        event_type: "progress",
        message: "Rendering concept.",
        progress: "45",
        status: "running",
      },
      label: "生成中",
      status: "running",
    },
    {
      event: {
        ...jobEventFixture,
        event_type: "completed",
        message: "Artifact ready.",
        progress: "100",
        status: "succeeded",
      },
      label: "已完成",
      status: "succeeded",
    },
  ])("renders $status generation progress", async ({ event, label, status }) => {
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const job = {
      ...generationJobFixture,
      status,
      updated_at: "2026-06-17T00:20:00Z",
    } satisfies GenerationJobResponse;
    const fetchMock = mockResumeWithGenerationState({ events: [event], job });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText(label)).toBeVisible();
    expect(screen.getByText(event.message)).toBeVisible();
    expect(screen.getByText("1 条事件")).toBeVisible();
    expect(screen.getByRole("button", { name: "刷新状态" })).toBeEnabled();
    expect(screen.queryByRole("button", { name: "重试生成" })).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getGetJobJobsJobIdGetUrl("job-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListEventsJobsJobIdEventsGetUrl("job-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListFeedbackWorkspacesWorkspaceIdFeedbackGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getListExportsWorkspacesWorkspaceIdExportsGetUrl("workspace-1")}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("refreshes compact operations status without exposing secrets", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const fetchMock = mockResumeWithGenerationState({})
      .mockResolvedValueOnce(jsonResponse([generationJobFixture]))
      .mockResolvedValueOnce(jsonResponse(generationJobFixture))
      .mockResolvedValueOnce(jsonResponse([jobEventFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(guardedHostedOperationsStatusFixture));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("排队中")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "刷新状态" }));

    expect(await screen.findByText("运维状态")).toBeVisible();
    expect(screen.getByText("Provider bfl")).toBeVisible();
    expect(screen.getByText("Worker ok")).toBeVisible();
    expect(screen.getByText("Guard 25/day · 4/min · <= 0.7500")).toBeVisible();
    expect(document.body.textContent).not.toMatch(/api[_-]?key|secret|[A-Z]:\\/i);
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getProviderStatusOperationsProviderStatusGetUrl()}`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("renders blocked hosted provider state while keeping local mode available", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, secondArtifactFixture],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture],
    })
      .mockResolvedValueOnce(jsonResponse([succeededJob]))
      .mockResolvedValueOnce(jsonResponse(succeededJob))
      .mockResolvedValueOnce(jsonResponse([jobEventFixture]))
      .mockResolvedValueOnce(jsonResponse([artifactFixture, secondArtifactFixture]))
      .mockResolvedValueOnce(jsonResponse([versionFixture, secondVersionFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(operationsStatusFixture));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "刷新状态" }));

    expect(await screen.findByText("生成模式")).toBeVisible();
    expect(screen.getByRole("button", { name: "本地概念" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: "本地概念" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "BFL 托管" })).toBeDisabled();
    expect(screen.getByText("托管调用开关关闭")).toBeVisible();
    expect(screen.getByText("BFL 凭据未配置")).toBeVisible();
    expect(document.body.textContent).not.toMatch(/api[_-]?key|secret|[A-Z]:\\/i);
  });

  it("submits selected hosted provider intent for child iterations", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const iterationJob = {
      ...generationJobFixture,
      id: "job-hosted-iteration-1",
      idempotency_key: "iteration-version-1-123",
      model: "flux-2-pro-preview",
      provider: "bfl",
      status: "queued",
      updated_at: "2026-06-17T00:36:00Z",
    } satisfies GenerationJobResponse;
    const iterationResult: GenerationJobSubmissionResponse = {
      idempotent_reused: false,
      job: iterationJob,
      queued: {
        job_id: "job-hosted-iteration-1",
        task_id: null,
        task_name: "caragent_worker.generate_2d_concept_job",
      },
    };
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, secondArtifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture],
    })
      .mockResolvedValueOnce(jsonResponse([succeededJob]))
      .mockResolvedValueOnce(jsonResponse(succeededJob))
      .mockResolvedValueOnce(jsonResponse([jobEventFixture]))
      .mockResolvedValueOnce(jsonResponse([artifactFixture, secondArtifactFixture]))
      .mockResolvedValueOnce(jsonResponse([versionFixture, secondVersionFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(guardedHostedOperationsStatusFixture))
      .mockResolvedValueOnce(jsonResponse(iterationResult, 201))
      .mockResolvedValueOnce(jsonResponse([iterationJob, succeededJob]))
      .mockResolvedValueOnce(jsonResponse(iterationJob))
      .mockResolvedValueOnce(jsonResponse([{ ...jobEventFixture, job_id: "job-hosted-iteration-1" }]))
      .mockResolvedValueOnce(jsonResponse([artifactFixture, secondArtifactFixture]))
      .mockResolvedValueOnce(jsonResponse([versionFixture, secondVersionFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(guardedHostedOperationsStatusFixture));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "刷新状态" }));

    expect(await screen.findByText("BFL 托管")).toBeVisible();
    expect(screen.getByText("25/day · 4/min")).toBeVisible();
    expect(screen.getByText("<= 0.7500 / job")).toBeVisible();
    expect(screen.getAllByText("概念预览").length).toBeGreaterThanOrEqual(1);
    await user.click(screen.getByRole("button", { name: "BFL 托管" }));
    expect(screen.getByRole("button", { name: "BFL 托管" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );

    await user.type(screen.getByRole("textbox", { name: "迭代需求" }), "加强车门光影");
    await user.click(screen.getByRole("button", { name: "生成子迭代" }));

    expect(
      await screen.findByText("子迭代已提交，父版本仍保留。"),
    ).toBeVisible();
    const iterationCall = fetchMock.mock.calls.find(([url]) =>
      String(url).includes("/versions/version-1/iterations"),
    );
    const iterationBody = JSON.parse(String((iterationCall?.[1] as RequestInit).body));
    expect(iterationBody).toMatchObject({
      brief_id: "brief-1",
      change_request: "加强车门光影",
      model: "flux-2-pro-preview",
      provider: "bfl",
      requested_by: "web-workbench",
    });
    expect(iterationBody).not.toHaveProperty("estimated_cost");
    expect(document.body.textContent).not.toMatch(/api[_-]?key|secret|[A-Z]:\\/i);
  });

  it("cancels queued generation jobs and removes cancel for terminal states", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const canceledJob = {
      ...generationJobFixture,
      metadata: {
        operations: {
          failure_category: "canceled",
          reason: "user_request",
          requested_by: "web-workbench",
        },
      },
      status: "canceled",
      updated_at: "2026-06-17T00:35:00Z",
    } satisfies GenerationJobResponse;
    const cancelResult: GenerationJobCancelResponse = {
      job: canceledJob,
      queue_revoke: {
        detail: null,
        status: "revoked",
        task_id: "task-1",
      },
    };
    const fetchMock = mockResumeWithGenerationState({
      job: generationJobFixture,
    }).mockResolvedValueOnce(jsonResponse(cancelResult));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("排队中")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "取消生成" }));

    expect(await screen.findByText("已取消")).toBeVisible();
    expect(screen.queryByRole("button", { name: "取消生成" })).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getCancelJobJobsJobIdCancelPostUrl("job-1")}`,
      expect.objectContaining({ method: "POST" }),
    );
    const cancelCall = fetchMock.mock.calls.find(([url]) =>
      String(url).includes("/jobs/job-1/cancel"),
    );
    expect(JSON.parse(String((cancelCall?.[1] as RequestInit).body))).toEqual({
      reason: "user_request",
      requested_by: "web-workbench",
    });
  });

  it("renders structured failure metadata without leaking secret-like text", async () => {
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const failedJob = {
      ...failedJobFixture,
      metadata: {
        operations: {
          failure_category: "timeout",
          provider: "bfl",
          stage: "provider_generate",
        },
      },
    } satisfies GenerationJobResponse;
    const failedEvent = {
      ...jobEventFixture,
      event_type: "error",
      message: "Provider timed out.",
      metadata: {
        failure_category: "timeout",
        provider: "bfl",
        stage: "provider_generate",
      },
      status: "failed",
    } satisfies JobEventResponse;
    const fetchMock = mockResumeWithGenerationState({
      events: [failedEvent],
      job: failedJob,
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("失败")).toBeVisible();
    expect(screen.getByText("失败分类 timeout")).toBeVisible();
    expect(screen.getByText("阶段 provider_generate")).toBeVisible();
    expect(screen.getByText("Provider bfl")).toBeVisible();
    expect(document.body.textContent).not.toMatch(/api[_-]?key|secret|[A-Z]:\\/i);
  });

  it("renders non-retryable targeted edit failures without retry controls", async () => {
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const failedJob = {
      ...failedJobFixture,
      latest_error: "target not found",
      metadata: {
        operations: {
          blocked_reason: "target not found",
          edit_route: "deterministic_recomposition",
          failure_category: "targeted_edit_invalid",
          provider: "deterministic-recomposition",
          retry_eligible: false,
          stage: "recomposition_validation",
          target: { id: "missing-layer", type: "overlay_layer" },
        },
      },
    } satisfies GenerationJobResponse;
    const fetchMock = mockResumeWithGenerationState({ job: failedJob });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("失败")).toBeVisible();
    expect(screen.getByText("失败分类 targeted_edit_invalid")).toBeVisible();
    expect(screen.getByText("Route deterministic_recomposition")).toBeVisible();
    expect(screen.getByText("目标 overlay_layer:missing-layer")).toBeVisible();
    expect(screen.getAllByText("target not found").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("不可重试")).toBeVisible();
    expect(screen.queryByRole("button", { name: "重试局部编辑" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "重试生成" })).not.toBeInTheDocument();
  });

  it("renders failed progress and retries generation jobs", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const failedEvent = {
      ...jobEventFixture,
      event_type: "failed",
      message: "Provider timeout",
      status: "failed",
    };
    const retryJob = {
      ...generationJobFixture,
      status: "queued",
      updated_at: "2026-06-17T00:30:00Z",
    } satisfies GenerationJobResponse;
    const fetchMock = mockResumeWithGenerationState({
      events: [failedEvent],
      job: failedJobFixture,
    }).mockResolvedValueOnce(
      jsonResponse({
        idempotent_reused: false,
        job: retryJob,
        queued: {
          job_id: "job-1",
          task_id: null,
          task_name: "caragent_worker.generate_2d_concept_job",
        },
        retry_of_job_id: "job-1",
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("失败")).toBeVisible();
    expect(screen.getAllByText("Provider timeout").length).toBeGreaterThanOrEqual(1);
    await user.click(screen.getByRole("button", { name: "重试生成" }));

    expect(fetchMock).toHaveBeenNthCalledWith(
      12,
      `http://localhost:8000${getRetryGenerationJobJobsJobIdRetryPostUrl("job-1")}`,
      expect.objectContaining({ method: "POST" }),
    );
    const retryInit = fetchMock.mock.calls[11]?.[1] as RequestInit;
    expect(JSON.parse(String(retryInit.body))).toEqual({
      idempotency_key: "retry-job-1",
      requested_by: "web-workbench",
    });
  });

  it("renders 2D preview controls and switches version history locally", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, secondArtifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture],
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    expect(screen.getByText("Generated 2D concept preview.")).toBeVisible();
    expect(screen.getByText(/concept\.png/)).toBeVisible();
    expect(screen.getByText("100%")).toBeVisible();
    expect(screen.getAllByText("PreviewSpec 摘要").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("图层 2").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("安全区 2").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("警告 1").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("模板参考区")).toBeVisible();
    expect(screen.getByRole("button", { name: "文字/Logo 图层" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: "安全区" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );

    await user.click(screen.getByRole("button", { name: "安全区" }));
    expect(screen.getByRole("button", { name: "安全区" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getAllByText("door-main").length).toBeGreaterThanOrEqual(1);

    await user.click(screen.getByRole("button", { name: "版本 2" }));
    expect(screen.getByText("Second 2D concept preview.")).toBeVisible();
    expect(screen.getByText(/concept-alt\.png/)).toBeVisible();

    await user.click(screen.getByRole("button", { name: "放大预览" }));
    expect(screen.getByText("125%")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "前视" }));
    expect(screen.getByRole("button", { name: "前视" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    await user.click(screen.getByRole("button", { name: "重置预览" }));
    expect(screen.getByText("100%")).toBeVisible();
    expect(screen.getByText(messageFixture.content)).toBeVisible();
    expect(screen.getByDisplayValue("清爽赛博风")).toBeVisible();
    expect(
      fetchMock.mock.calls.some(
        ([url]) =>
          String(url).includes("/versions/version-2") ||
          String(url).includes("/selected-version"),
      ),
    ).toBe(false);
  });

  it("shows metadata lineage comparison and submits child iterations without overwriting parent", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const iterationJob = {
      ...generationJobFixture,
      id: "job-iteration-1",
      idempotency_key: "iteration-version-2-123",
      status: "queued",
      updated_at: "2026-06-17T00:32:00Z",
    } satisfies GenerationJobResponse;
    const iterationResult: GenerationJobSubmissionResponse = {
      idempotent_reused: false,
      job: iterationJob,
      queued: {
        job_id: "job-iteration-1",
        task_id: null,
        task_name: "caragent_worker.generate_2d_concept_job",
      },
    };
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, secondArtifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture],
    })
      .mockResolvedValueOnce(jsonResponse(iterationResult, 201))
      .mockResolvedValueOnce(jsonResponse([iterationJob, succeededJob]))
      .mockResolvedValueOnce(jsonResponse(iterationJob))
      .mockResolvedValueOnce(jsonResponse([{ ...jobEventFixture, job_id: "job-iteration-1" }]))
      .mockResolvedValueOnce(jsonResponse([artifactFixture, secondArtifactFixture]))
      .mockResolvedValueOnce(jsonResponse([versionFixture, secondVersionFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "版本 2" }));

    expect(screen.getByText("谱系深度 1")).toBeVisible();
    expect(screen.getByText("父版本: 版本 1")).toBeVisible();
    expect(screen.getByText("当前版本: 版本 2")).toBeVisible();
    expect(screen.getByText("仅对比元数据和参数")).toBeVisible();
    expect(screen.getByText("coverage")).toBeVisible();
    expect(screen.getByText("balanced side coverage -> door focus")).toBeVisible();
    expect(screen.getByText(messageFixture.content)).toBeVisible();
    expect(screen.getByDisplayValue("清爽赛博风")).toBeVisible();
    expect(screen.getByText("素材")).toBeVisible();

    await user.type(screen.getByRole("textbox", { name: "迭代需求" }), "把门板角色放大");
    await user.click(screen.getByRole("button", { name: "生成子迭代" }));

    expect(
      await screen.findByText("子迭代已提交，父版本仍保留。"),
    ).toBeVisible();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getSubmitGenerationIterationJobWorkspacesWorkspaceIdVersionsVersionIdIterationsPostUrl(
        "workspace-1",
        "version-2",
      )}`,
      expect.objectContaining({ method: "POST" }),
    );
    const iterationCall = fetchMock.mock.calls.find(([url]) =>
      String(url).includes("/versions/version-2/iterations"),
    );
    const iterationBody = JSON.parse(String((iterationCall?.[1] as RequestInit).body));
    expect(iterationBody).toMatchObject({
      brief_id: "brief-1",
      change_request: "把门板角色放大",
      parameter_overrides: {},
      requested_by: "web-workbench",
    });
    expect(iterationBody).not.toHaveProperty("edit_intent");
    expect(iterationBody.idempotency_key).toMatch(/^iteration-version-2-\d+$/);
    expect(
      fetchMock.mock.calls.some(
        ([url, init]) =>
          String(url).includes("/versions/version-1") &&
          (init as RequestInit | undefined)?.method !== "GET",
      ),
    ).toBe(false);
    expect(
      fetchMock.mock.calls.some(
        ([url, init]) =>
          String(url).includes("/versions/version-2") &&
          !String(url).includes("/iterations") &&
          (init as RequestInit | undefined)?.method !== "GET",
      ),
    ).toBe(false);
  });

  it("compares targeted recomposition child versions with metadata-backed region highlights", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:35:00Z",
    } satisfies GenerationJobResponse;
    const targetedArtifact = {
      ...secondArtifactFixture,
      id: "artifact-targeted-recomposition",
      object_key: "workspaces/workspace-1/generated_image/artifact-targeted/concept.png",
      version_id: "version-targeted-recomposition",
    } satisfies ArtifactResponse;
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, targetedArtifact],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture, targetedRecompositionVersionFixture],
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    expect(screen.queryByRole("button", { name: "对比 版本 2" })).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "对比 局部编辑 1" }));

    expect(screen.getByText("局部编辑对比")).toBeVisible();
    expect(screen.getByText("父版本: 版本 1")).toBeVisible();
    expect(screen.getByText("当前版本: 局部编辑 1")).toBeVisible();
    expect(screen.getByText("路线 本地重组")).toBeVisible();
    expect(screen.getByText("Route deterministic_recomposition")).toBeVisible();
    expect(screen.getByText("目标 overlay_layer:text-1")).toBeVisible();
    expect(screen.getByText("Prompt 把门板文字上移")).toBeVisible();
    expect(screen.getByText("改动字段 text, y")).toBeVisible();
    expect(screen.getByText("区域 32% / 47% / 34% / 24%")).toBeVisible();
    expect(screen.getByLabelText("改动区域 overlay_layer:text-1")).toBeVisible();
    expect(screen.getByText("区域高亮来自编辑元数据")).toBeVisible();
  });

  it("compares provider masked children and handles missing parents gracefully", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:38:00Z",
    } satisfies GenerationJobResponse;
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      job: succeededJob,
      versions: [versionFixture, targetedProviderVersionFixture, orphanTargetedVersionFixture],
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "对比 托管局部编辑" }));

    expect(screen.getByText("路线 托管遮罩生成")).toBeVisible();
    expect(screen.getByText("Route provider_masked_generation")).toBeVisible();
    expect(screen.getByText("Provider bfl")).toBeVisible();
    expect(screen.getByText("Model flux-2-pro-preview")).toBeVisible();
    expect(screen.getByText("Cost 0.6500")).toBeVisible();
    expect(screen.getByText("目标 safe_zone:rear-quarter")).toBeVisible();
    expect(screen.getByText("Prompt 重绘后翼子板角色表情")).toBeVisible();

    await user.click(screen.getByRole("button", { name: "对比 孤立局部编辑" }));

    expect(screen.getByText("父版本: 未加载")).toBeVisible();
    expect(screen.getByText("当前版本: 孤立局部编辑")).toBeVisible();
  });

  it("submits targeted edit intent from selected preview layers", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const iterationJob = {
      ...generationJobFixture,
      id: "job-targeted-iteration-1",
      idempotency_key: "iteration-version-1-123",
      status: "queued",
      updated_at: "2026-06-17T00:36:00Z",
    } satisfies GenerationJobResponse;
    const iterationResult: GenerationJobSubmissionResponse = {
      idempotent_reused: false,
      job: iterationJob,
      queued: {
        job_id: "job-targeted-iteration-1",
        task_id: null,
        task_name: "caragent_worker.generate_2d_concept_job",
      },
    };
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      job: succeededJob,
      versions: [versionFixture],
    })
      .mockResolvedValueOnce(jsonResponse(iterationResult, 201))
      .mockResolvedValueOnce(jsonResponse([iterationJob, succeededJob]))
      .mockResolvedValueOnce(jsonResponse(iterationJob))
      .mockResolvedValueOnce(jsonResponse([{ ...jobEventFixture, job_id: "job-targeted-iteration-1" }]))
      .mockResolvedValueOnce(jsonResponse([artifactFixture]))
      .mockResolvedValueOnce(jsonResponse([versionFixture]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("2D 概念预览")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "局部编辑" }));
    await user.click(screen.getByRole("button", { name: "安全区" }));
    await user.click(screen.getByRole("button", { name: "选择安全区 door-main" }));
    expect(screen.getByText("已选 safe_zone: door-main")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "选择图层 text-1" }));
    await user.click(screen.getByRole("button", { name: "显示编辑遮罩" }));
    expect(screen.getByText("已选 overlay_layer: text-1")).toBeVisible();
    expect(screen.getByText("编辑遮罩预览")).toBeVisible();

    await user.type(screen.getByRole("textbox", { name: "迭代需求" }), "把门板文字上移");
    await user.click(screen.getByRole("button", { name: "生成子迭代" }));

    expect(
      await screen.findByText("子迭代已提交，父版本仍保留。"),
    ).toBeVisible();
    const iterationCall = fetchMock.mock.calls.find(([url]) =>
      String(url).includes("/versions/version-1/iterations"),
    );
    const iterationBody = JSON.parse(String((iterationCall?.[1] as RequestInit).body));
    expect(iterationBody).toMatchObject({
      brief_id: "brief-1",
      change_request: "把门板文字上移",
      edit_intent: {
        mask: {
          artifact_id: "artifact-1",
          content_type: "image/png",
          height: 768,
          width: 1536,
        },
        mode: "targeted_edit",
        parent_version_id: "version-1",
        prompt_delta: {
          instructions: ["把门板文字上移"],
          summary: "把门板文字上移",
        },
        region: {
          height: 0.24,
          type: "rectangle",
          unit: "normalized",
          width: 0.34,
          x: 0.32,
          y: 0.47,
        },
        route_preference: "deterministic_recomposition",
        schema_version: 1,
        target: {
          id: "text-1",
          type: "overlay_layer",
        },
      },
      parameter_overrides: {},
      requested_by: "web-workbench",
    });
    expect(iterationBody.idempotency_key).toMatch(/^iteration-version-1-\d+$/);
  });

  it("submits durable feedback scoped to the selected version and renders feedback history", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const savedFeedback = {
      ...feedbackFixture,
      comment: "通过，继续强化粉色侧裙。",
      id: "feedback-2",
      rating: 4,
      updated_at: "2026-06-17T00:48:00Z",
    } satisfies FeedbackResponse;
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, secondArtifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      feedback: [feedbackFixture],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture],
    }).mockResolvedValueOnce(jsonResponse(savedFeedback, 201));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("反馈历史")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "版本 2" }));
    expect(screen.getByText("这个方向可以继续。")).toBeVisible();
    expect(screen.getByText("评分 5")).toBeVisible();

    await user.click(screen.getByRole("button", { name: "评分 4" }));
    await user.click(screen.getByRole("button", { name: "通过" }));
    await user.type(screen.getByRole("textbox", { name: "反馈评论" }), "通过，继续强化粉色侧裙。");
    await user.click(screen.getByRole("button", { name: "提交反馈" }));

    expect(await screen.findByText("反馈已保存。")).toBeVisible();
    expect(screen.getByText("通过，继续强化粉色侧裙。")).toBeVisible();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getCreateFeedbackWorkspacesWorkspaceIdVersionsVersionIdFeedbackPostUrl(
        "workspace-1",
        "version-2",
      )}`,
      expect.objectContaining({ method: "POST" }),
    );
    const feedbackCall = fetchMock.mock.calls.find(([url]) =>
      String(url).includes("/versions/version-2/feedback"),
    );
    expect(JSON.parse(String((feedbackCall?.[1] as RequestInit).body))).toEqual({
      approval_state: "approved",
      comment: "通过，继续强化粉色侧裙。",
      metadata: { source: "web-workbench" },
      rating: 4,
    });
    expect(
      fetchMock.mock.calls.some(([url]) => String(url).includes("/versions/version-1/feedback")),
    ).toBe(false);
    expect(localStorage.getItem("caragent.workbench.workspaceId")).toBe("workspace-1");
    expect(localStorage.getItem("caragent.workbench.briefId")).toBe("brief-1");
  });

  it("creates selected-version concept exports with manifest preview and deferred production gates", async () => {
    const user = userEvent.setup();
    localStorage.setItem("caragent.workbench.workspaceId", "workspace-1");
    localStorage.setItem("caragent.workbench.briefId", "brief-1");
    const succeededJob = {
      ...generationJobFixture,
      status: "succeeded",
      updated_at: "2026-06-17T00:25:00Z",
    } satisfies GenerationJobResponse;
    const savedExport = {
      ...exportFixture,
      format: "jpg",
      id: "export-2",
      updated_at: "2026-06-17T00:55:00Z",
    } satisfies ExportResponse;
    const fetchMock = mockResumeWithGenerationState({
      artifacts: [artifactFixture, secondArtifactFixture],
      events: [
        {
          ...jobEventFixture,
          event_type: "completed",
          message: "Artifact ready.",
          progress: "100",
          status: "succeeded",
        },
      ],
      exports: [exportFixture],
      job: succeededJob,
      versions: [versionFixture, secondVersionFixture],
    }).mockResolvedValueOnce(jsonResponse(savedExport, 201));
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);

    expect(await screen.findByText("导出历史")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "版本 2" }));
    expect(screen.getByText("概念预览，不是生产印刷文件。")).toBeVisible();
    expect(screen.getByText("client-review")).toBeVisible();
    expect(screen.getByText("Concept preview only, not print-ready.")).toBeVisible();
    expect(screen.getAllByText("PreviewSpec 摘要").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("图层 2").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("安全区 2").length).toBeGreaterThanOrEqual(1);
    expect(document.body.textContent).not.toContain("production-ready");
    expect(document.body.textContent).not.toContain("生产就绪");
    expect(screen.getByRole("button", { name: "生产导出后续开放" })).toBeDisabled();

    await user.click(screen.getByRole("button", { name: "JPG" }));
    await user.click(screen.getByRole("button", { name: "创建概念导出" }));

    expect(await screen.findByText("概念导出已记录。")).toBeVisible();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000${getCreateExportWorkspacesWorkspaceIdVersionsVersionIdExportsPostUrl(
        "workspace-1",
        "version-2",
      )}`,
      expect.objectContaining({ method: "POST" }),
    );
    const exportCall = fetchMock.mock.calls.find(([url]) =>
      String(url).includes("/versions/version-2/exports"),
    );
    const exportBody = JSON.parse(String((exportCall?.[1] as RequestInit).body));
    expect(exportBody).toEqual({
      artifact_id: "artifact-2",
      concept_label: "client-review",
      format: "jpg",
      manifest: {
        disclaimer: "概念预览，不是生产印刷文件。",
        source: "web-workbench",
        source_artifact_object_key: secondArtifactFixture.object_key,
        version_id: "version-2",
      },
    });
    expect(JSON.stringify(exportBody)).not.toMatch(/[A-Z]:\\|api[_-]?key|secret/i);
    expect(
      fetchMock.mock.calls.some(([url]) => String(url).includes("/versions/version-1/exports")),
    ).toBe(false);
  });
});
