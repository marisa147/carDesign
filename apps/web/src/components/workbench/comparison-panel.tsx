import type { DesignVersionResponse } from "@caragent/contracts";
import type { CSSProperties } from "react";

import { Badge } from "@/components/ui/badge";
import { useWorkbenchStore } from "@/lib/workbench/store";

interface ComparisonPanelProps {
  versions: DesignVersionResponse[];
}

export function ComparisonPanel({ versions }: ComparisonPanelProps) {
  const isVersionComparisonMode = useWorkbenchStore(
    (state) => state.isVersionComparisonMode,
  );
  const selectedComparisonChildId = useWorkbenchStore(
    (state) => state.selectedComparisonChildId,
  );
  const selectedVersionId = useWorkbenchStore((state) => state.selectedVersionId);
  const selectedVersion = selectVersion(
    versions,
    isVersionComparisonMode ? selectedComparisonChildId : selectedVersionId,
  );
  const parentVersion = selectedVersion?.parent_version_id
    ? versions.find((version) => version.id === selectedVersion.parent_version_id) ?? null
    : null;
  const targetedComparison = readTargetedComparison(selectedVersion);
  const differences = compareParameters(
    parentVersion?.parameters ?? {},
    selectedVersion?.parameters ?? {},
  );

  if (!selectedVersion) {
    return (
      <div className="rounded-md border border-dashed border-border bg-muted p-3 text-sm text-secondary-foreground">
        生成版本后可查看谱系和参数差异。
      </div>
    );
  }

  return (
    <div className="grid gap-3 rounded-md border border-border bg-background p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold">
            {targetedComparison ? "局部编辑对比" : "版本对比"}
          </p>
          <p className="mt-1 text-xs text-secondary-foreground">
            谱系深度 {selectedVersion.lineage_depth}
          </p>
        </div>
        {targetedComparison ? (
          <Badge variant="primary">路线 {targetedComparison.routeLabel}</Badge>
        ) : (
          <Badge variant="muted">仅对比元数据和参数</Badge>
        )}
      </div>

      <div className="grid gap-1 text-sm">
        <p>父版本: {formatParentTitle(selectedVersion, parentVersion)}</p>
        <p>当前版本: {selectedVersion.title ?? selectedVersion.id}</p>
      </div>

      {targetedComparison ? (
        <TargetedComparisonDetails comparison={targetedComparison} />
      ) : null}

      <div className="grid gap-2">
        {differences.length > 0 ? (
          differences.map((difference) => (
            <div
              className="grid grid-cols-[minmax(80px,0.45fr)_minmax(0,1fr)] gap-2 rounded-md border border-border bg-card px-2 py-1.5 text-xs"
              key={difference.key}
            >
              <span className="font-medium">{difference.key}</span>
              <span className="break-words text-secondary-foreground">
                {difference.before} -&gt; {difference.after}
              </span>
            </div>
          ))
        ) : (
          <p className="rounded-md border border-border bg-card px-2 py-1.5 text-xs text-secondary-foreground">
            参数未变化
          </p>
        )}
      </div>
    </div>
  );
}

function TargetedComparisonDetails({
  comparison,
}: {
  comparison: TargetedComparison;
}) {
  return (
    <div className="grid gap-3 text-xs">
      <div className="grid gap-1 rounded-md border border-border bg-card px-3 py-2">
        <p>Route {comparison.route}</p>
        {comparison.targetSummary ? <p>目标 {comparison.targetSummary}</p> : null}
        {comparison.promptSummary ? <p>Prompt {comparison.promptSummary}</p> : null}
        {comparison.changedFields.length > 0 ? (
          <p>改动字段 {comparison.changedFields.join(", ")}</p>
        ) : null}
        {comparison.maskArtifactId ? <p>Mask {comparison.maskArtifactId}</p> : null}
        {comparison.provider ? <p>Provider {comparison.provider}</p> : null}
        {comparison.model ? <p>Model {comparison.model}</p> : null}
        {comparison.cost ? <p>Cost {comparison.cost}</p> : null}
      </div>
      <ChangedRegionMap
        region={comparison.region}
        targetSummary={comparison.targetSummary}
      />
    </div>
  );
}

function ChangedRegionMap({
  region,
  targetSummary,
}: {
  region: TargetedRegion | null;
  targetSummary: string | null;
}) {
  if (!region) {
    return (
      <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-secondary-foreground">
        未记录改动区域
      </p>
    );
  }

  return (
    <div className="grid gap-2">
      <div
        aria-label={`改动区域 ${targetSummary ?? "unknown"}`}
        className="relative aspect-[2/1] min-h-28 overflow-hidden rounded-md border border-border bg-muted"
        role="img"
      >
        <div className="absolute left-[9%] top-[36%] h-[36%] w-[82%] rounded-[48px] border-2 border-foreground bg-card" />
        <div className="absolute left-[22%] top-[28%] h-[16%] w-[42%] border-2 border-foreground bg-background" />
        <div className="absolute left-[20%] top-[58%] h-[18%] w-[9%] rounded-full bg-foreground" />
        <div className="absolute left-[72%] top-[58%] h-[18%] w-[9%] rounded-full bg-foreground" />
        <div
          className="pointer-events-none absolute rounded border-2 border-destructive bg-destructive/20"
          style={regionStyle(region)}
        />
      </div>
      <p>区域 {formatRegion(region)}</p>
      <p className="text-secondary-foreground">区域高亮来自编辑元数据</p>
    </div>
  );
}

function selectVersion(
  versions: DesignVersionResponse[],
  selectedVersionId: string | null,
): DesignVersionResponse | null {
  return versions.find((version) => version.id === selectedVersionId) ?? versions[0] ?? null;
}

function formatParentTitle(
  selectedVersion: DesignVersionResponse,
  parentVersion: DesignVersionResponse | null,
): string {
  if (parentVersion) {
    return parentVersion.title ?? parentVersion.id;
  }

  return selectedVersion.parent_version_id ? "未加载" : "无";
}

function compareParameters(
  parentParameters: Record<string, unknown>,
  selectedParameters: Record<string, unknown>,
) {
  return Array.from(
    new Set([...Object.keys(parentParameters), ...Object.keys(selectedParameters)]),
  )
    .sort()
    .filter((key) => formatValue(parentParameters[key]) !== formatValue(selectedParameters[key]))
    .map((key) => ({
      after: formatValue(selectedParameters[key]),
      before: formatValue(parentParameters[key]),
      key,
    }));
}

function formatValue(value: unknown): string {
  if (value === undefined || value === null) {
    return "-";
  }
  if (typeof value === "string") {
    return value;
  }
  return JSON.stringify(value);
}

interface TargetedComparison {
  changedFields: string[];
  cost: string | null;
  maskArtifactId: string | null;
  model: string | null;
  promptSummary: string | null;
  provider: string | null;
  region: TargetedRegion | null;
  route: string;
  routeLabel: string;
  targetSummary: string | null;
}

interface TargetedRegion {
  height: number;
  width: number;
  x: number;
  y: number;
}

function readTargetedComparison(
  version: DesignVersionResponse | null,
): TargetedComparison | null {
  if (!version || !version.parent_version_id) {
    return null;
  }

  const parameters = version.parameters;
  const editIntent = asRecord(parameters.edit_intent);
  const promptPayload = asRecord(parameters.prompt_payload);
  const maskEdit = asRecord(promptPayload?.mask_edit);
  const sources = [parameters, editIntent, maskEdit].filter(
    (source): source is Record<string, unknown> => source !== null,
  );
  const route = findString(sources, "edit_route") ?? findString(sources, "route");
  const target = findRecord(sources, "target");
  const region = readTargetedRegion(findRecord(sources, "region"));
  const promptDelta = findRecord(sources, "prompt_delta");
  const promptSummary =
    readNullableString(promptDelta?.summary) ??
    readStringArray(promptDelta?.instructions)[0] ??
    null;
  const targetSummary = formatTargetSummary(target);

  if (!route && !targetSummary && !region && !promptSummary) {
    return null;
  }

  return {
    changedFields: readStringArray(parameters.changed_fields),
    cost:
      readNullableString(parameters.actual_cost) ??
      readNullableString(parameters.estimated_cost),
    maskArtifactId:
      findString(sources, "mask_artifact_id") ??
      readNullableString(asRecord(parameters.mask)?.artifact_id),
    model: readNullableString(parameters.model),
    promptSummary,
    provider: readNullableString(parameters.provider),
    region,
    route: route ?? "unknown",
    routeLabel: formatRouteLabel(route),
    targetSummary,
  };
}

function findRecord(
  sources: Array<Record<string, unknown>>,
  key: string,
): Record<string, unknown> | null {
  for (const source of sources) {
    const value = asRecord(source[key]);
    if (value) {
      return value;
    }
  }
  return null;
}

function findString(sources: Array<Record<string, unknown>>, key: string): string | null {
  for (const source of sources) {
    const value = readNullableString(source[key]);
    if (value) {
      return value;
    }
  }
  return null;
}

function formatRouteLabel(route: string | null): string {
  if (route === "deterministic_recomposition") {
    return "本地重组";
  }
  if (route === "provider_masked_generation") {
    return "托管遮罩生成";
  }
  return "未知路线";
}

function formatTargetSummary(target: Record<string, unknown> | null): string | null {
  const type = readNullableString(target?.type);
  const id = readNullableString(target?.id);
  if (!type || !id) {
    return null;
  }
  return `${type}:${id}`;
}

function readTargetedRegion(region: Record<string, unknown> | null): TargetedRegion | null {
  const x = readNumber(region?.x);
  const y = readNumber(region?.y);
  const width = readNumber(region?.width);
  const height = readNumber(region?.height);
  if (x === null || y === null || width === null || height === null) {
    return null;
  }
  return {
    height: clampUnit(height),
    width: clampUnit(width),
    x: clampUnit(x),
    y: clampUnit(y),
  };
}

function regionStyle(region: TargetedRegion): CSSProperties {
  return {
    height: `${region.height * 100}%`,
    left: `${region.x * 100}%`,
    top: `${region.y * 100}%`,
    width: `${region.width * 100}%`,
  };
}

function formatRegion(region: TargetedRegion): string {
  return [region.x, region.y, region.width, region.height]
    .map((value) => `${Math.round(value * 100)}%`)
    .join(" / ");
}

function readStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string" && item.length > 0);
}

function readNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function readNullableString(value: unknown): string | null {
  if (typeof value === "string" && value.length > 0) {
    return value;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  return null;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function clampUnit(value: number): number {
  return Math.min(1, Math.max(0, value));
}
