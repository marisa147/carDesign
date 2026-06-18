"use client";

import type {
  GenerationJobResponse,
  JobEventResponse,
  OperationsProviderStatusResponse,
} from "@caragent/contracts";
import { Ban, Loader2, RefreshCw, RotateCcw, ShieldAlert } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { REFERENCE_ROLE_OPTIONS } from "@/lib/api/generation";
import { BFL_PROVIDER_ID, getProviderOption, normalizeProviderStatus } from "@/lib/api/operations";

interface ProgressPanelProps {
  events: JobEventResponse[];
  isCanceling: boolean;
  isLoading: boolean;
  isRetrying: boolean;
  job: GenerationJobResponse | null;
  operationsStatus: OperationsProviderStatusResponse | null;
  onCancel: () => void;
  onRefresh: () => void;
  onRetry: () => void;
}

export function ProgressPanel({
  events,
  isCanceling,
  isLoading,
  isRetrying,
  job,
  operationsStatus,
  onCancel,
  onRefresh,
  onRetry,
}: ProgressPanelProps) {
  if (!job) {
    return (
      <div aria-live="polite" className="grid gap-3 text-sm">
        <div className="flex items-center justify-between gap-3">
          <span className="text-secondary-foreground">当前任务</span>
          <Badge variant="muted">等待提交</Badge>
        </div>
        <p className="text-secondary-foreground">
          生成任务提交后，这里会显示 queued、running、succeeded 或 failed 状态和最近事件。
        </p>
        <OperationsStatusSummary operationsStatus={operationsStatus} />
        <Button disabled={isLoading} onClick={onRefresh} type="button" variant="outline">
          {isLoading ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw aria-hidden="true" className="h-4 w-4" />
          )}
          刷新状态
        </Button>
      </div>
    );
  }

  const status = getStatusView(job.status);
  const latestEvent = events.at(-1);
  const operationsMetadata = getOperationsMetadata(job, latestEvent);
  const failureCategory = getMetadataString(operationsMetadata, "failure_category");
  const failureStage = getMetadataString(operationsMetadata, "stage");
  const failureProvider = getMetadataString(operationsMetadata, "provider");
  const blockedReason = getMetadataString(operationsMetadata, "blocked_reason");
  const editRoute = getMetadataString(operationsMetadata, "edit_route");
  const retryEligible = getMetadataBoolean(operationsMetadata, "retry_eligible");
  const targetSummary = getTargetSummary(operationsMetadata);
  const referenceDiagnostics = getReferenceDiagnostics(job, latestEvent, operationsMetadata);
  const canCancel = job.status === "queued" || job.status === "running";
  const canRetry = job.status === "failed" && retryEligible !== false;
  const retryLabel = editRoute ? "重试局部编辑" : "重试生成";

  return (
    <div aria-live="polite" className="grid gap-3 text-sm">
      <div className="flex items-center justify-between gap-3">
        <span className="text-secondary-foreground">当前任务</span>
        <Badge variant={status.variant}>{status.label}</Badge>
      </div>
      <div className="rounded-md border border-border bg-muted p-3">
        <p className="font-medium">{job.operation}</p>
        {latestEvent ? (
          <p className="mt-1 text-secondary-foreground">
            {sanitizeDiagnosticText(latestEvent.message ?? "暂无事件")}
          </p>
        ) : (
          <p className="mt-1 text-secondary-foreground">暂无事件</p>
        )}
        {job.latest_error ? (
          <p className="mt-2 text-destructive">
            {sanitizeDiagnosticText(job.latest_error)}
          </p>
        ) : null}
      </div>
      <OperationsStatusSummary operationsStatus={operationsStatus} />
      {failureCategory ? (
        <div className="grid gap-1 rounded-md border border-border bg-background p-3 text-xs">
          <span className="font-medium">失败分类 {failureCategory}</span>
          {failureStage ? (
            <span className="text-secondary-foreground">阶段 {failureStage}</span>
          ) : null}
          {failureProvider ? (
            <span className="text-secondary-foreground">Provider {failureProvider}</span>
          ) : null}
          {editRoute ? (
            <span className="text-secondary-foreground">Route {editRoute}</span>
          ) : null}
          {targetSummary ? (
            <span className="text-secondary-foreground">目标 {targetSummary}</span>
          ) : null}
          {blockedReason ? (
            <span className="text-secondary-foreground">{blockedReason}</span>
          ) : null}
          {retryEligible === false ? (
            <span className="text-secondary-foreground">不可重试</span>
          ) : null}
        </div>
      ) : null}
      {referenceDiagnostics ? (
        <ReferenceDiagnosticsSummary diagnostics={referenceDiagnostics} />
      ) : null}
      <div>
        <p className="mb-2 text-xs font-medium text-secondary-foreground">
          {events.length} 条事件
        </p>
        <ul className="grid gap-2">
          {events.map((event) => (
            <li
              className="rounded-md border border-border bg-background px-3 py-2 text-xs"
              key={event.id}
            >
              <span className="font-medium">{event.status}</span>
              <span className="text-secondary-foreground">
                {" "}
                · {sanitizeDiagnosticText(event.message ?? "")}
              </span>
            </li>
          ))}
        </ul>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button disabled={isLoading} onClick={onRefresh} type="button" variant="outline">
          {isLoading ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw aria-hidden="true" className="h-4 w-4" />
          )}
          刷新状态
        </Button>
        {canCancel ? (
          <Button disabled={isCanceling} onClick={onCancel} type="button" variant="outline">
            {isCanceling ? (
              <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
            ) : (
              <Ban aria-hidden="true" className="h-4 w-4" />
            )}
            取消生成
          </Button>
        ) : null}
        {canRetry ? (
          <Button disabled={isRetrying} onClick={onRetry} type="button" variant="outline">
            {isRetrying ? (
              <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw aria-hidden="true" className="h-4 w-4" />
            )}
            {retryLabel}
          </Button>
        ) : null}
      </div>
    </div>
  );
}

function getStatusView(status: string): {
  label: string;
  variant: "default" | "muted" | "primary" | "warning";
} {
  if (status === "queued") {
    return { label: "排队中", variant: "muted" };
  }

  if (status === "running") {
    return { label: "生成中", variant: "primary" };
  }

  if (status === "succeeded") {
    return { label: "已完成", variant: "primary" };
  }

  if (status === "failed") {
    return { label: "失败", variant: "warning" };
  }

  if (status === "canceled") {
    return { label: "已取消", variant: "muted" };
  }

  return { label: status, variant: "default" };
}

function OperationsStatusSummary({
  operationsStatus,
}: {
  operationsStatus: OperationsProviderStatusResponse | null;
}) {
  const provider = operationsStatus?.provider;
  const worker = operationsStatus?.worker;
  const queue = operationsStatus?.queue;
  const normalizedStatus = normalizeProviderStatus(operationsStatus);
  const recentFailure = normalizedStatus.recentFailures[0];

  return (
    <div className="grid gap-2 rounded-md border border-border bg-background p-3 text-xs">
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-foreground">运维状态</span>
        <Badge variant={worker?.status === "ok" ? "primary" : "muted"}>
          {worker?.status ?? "未刷新"}
        </Badge>
      </div>
      {operationsStatus ? (
        <div className="grid gap-1 text-secondary-foreground">
          <span>Provider {sanitizeDiagnosticText(provider?.active_mode ?? "unknown")}</span>
          <span>Worker {sanitizeDiagnosticText(worker?.status ?? "unknown")}</span>
          <span>{formatGuardSummary(operationsStatus, normalizedStatus)}</span>
          <span>Queue {sanitizeDiagnosticText(queue?.status ?? "unknown")}</span>
          {recentFailure ? (
            <span>
              最近失败 {recentFailure.failureKind ?? recentFailure.failureCategory}
            </span>
          ) : null}
        </div>
      ) : (
        <span className="text-secondary-foreground">未刷新</span>
      )}
    </div>
  );
}

function formatGuardSummary(
  status: OperationsProviderStatusResponse,
  normalizedStatus: ReturnType<typeof normalizeProviderStatus>,
): string {
  const provider = status.provider;
  if (provider.hosted_quota_guard_enabled) {
    return `Guard ${normalizedStatus.guardLabel} · ${normalizedStatus.maxCostLabel.replace(
      " / job",
      "",
    )}`;
  }

  const bflOption = getProviderOption(normalizedStatus, BFL_PROVIDER_ID);
  if (bflOption?.blockedReasons.length) {
    return `Guard ${bflOption.blockedReasons[0]}`;
  }

  return "Guard local bypass";
}

interface ReferenceDiagnostics {
  includedCount: number;
  omittedCount: number;
  roleCounts: Array<{ count: number; label: string; role: string }>;
  unsupportedRoleLabels: string[];
  warningCount: number;
}

function ReferenceDiagnosticsSummary({
  diagnostics,
}: {
  diagnostics: ReferenceDiagnostics;
}) {
  const hasWarnings =
    diagnostics.warningCount > 0 ||
    diagnostics.omittedCount > 0 ||
    diagnostics.unsupportedRoleLabels.length > 0;

  return (
    <div className="grid gap-2 rounded-md border border-warning/30 bg-warning/10 p-3 text-xs text-warning">
      <div className="flex items-center gap-1 font-medium">
        <ShieldAlert aria-hidden="true" className="h-4 w-4" />
        {hasWarnings ? "引用受限" : "引用追踪"}
      </div>
      <div className="flex flex-wrap gap-2">
        <Badge variant={hasWarnings ? "warning" : "muted"}>
          已用引用 {diagnostics.includedCount}
        </Badge>
        {diagnostics.omittedCount > 0 ? (
          <Badge variant="warning">省略引用 {diagnostics.omittedCount}</Badge>
        ) : null}
        <Badge variant={hasWarnings ? "warning" : "muted"}>
          警告 {diagnostics.warningCount}
        </Badge>
        {diagnostics.roleCounts.map((entry) => (
          <Badge key={entry.role} variant="muted">
            {entry.label} {entry.count}
          </Badge>
        ))}
      </div>
      {diagnostics.unsupportedRoleLabels.length > 0 ? (
        <span>不支持角色 {diagnostics.unsupportedRoleLabels.join(", ")}</span>
      ) : null}
    </div>
  );
}

function getOperationsMetadata(
  job: GenerationJobResponse,
  latestEvent: JobEventResponse | undefined,
): Record<string, unknown> | null {
  const jobMetadata = asRecord(job.metadata);
  const jobOperations = asRecord(jobMetadata?.operations);
  if (jobOperations) {
    return jobOperations;
  }

  return asRecord(latestEvent?.metadata);
}

function getReferenceDiagnostics(
  job: GenerationJobResponse,
  latestEvent: JobEventResponse | undefined,
  operationsMetadata: Record<string, unknown> | null,
): ReferenceDiagnostics | null {
  const sources = [
    operationsMetadata,
    asRecord(job.metadata),
    asRecord(latestEvent?.metadata),
  ].filter((source): source is Record<string, unknown> => source !== null);
  if (sources.length === 0) {
    return null;
  }

  const roleCounts = getReferenceRoleCounts(sources);
  const usageItemCount = getReferenceUsageItemCount(sources);
  const includedCount = getStringArrayFromSources(
    sources,
    "included_reference_asset_ids",
  ).length;
  const omittedCount = getStringArrayFromSources(
    sources,
    "omitted_reference_asset_ids",
  ).length;
  const unsupportedRoleLabels = getStringArrayFromSources(
    sources,
    "unsupported_reference_roles",
  ).map(referenceRoleLabel);
  const warningCount = getNumberFromSources(sources, "reference_warning_count") ?? 0;
  const effectiveIncludedCount = Math.max(
    includedCount,
    usageItemCount,
    roleCounts.reduce((total, entry) => total + entry.count, 0),
  );

  if (
    effectiveIncludedCount === 0 &&
    omittedCount === 0 &&
    unsupportedRoleLabels.length === 0 &&
    warningCount === 0
  ) {
    return null;
  }

  return {
    includedCount: effectiveIncludedCount,
    omittedCount,
    roleCounts,
    unsupportedRoleLabels,
    warningCount,
  };
}

function getMetadataString(
  metadata: Record<string, unknown> | null,
  key: string,
): string | null {
  const value = metadata?.[key];
  if (typeof value !== "string") {
    return null;
  }

  const trimmedValue = value.trim();
  if (trimmedValue.length === 0) {
    return null;
  }

  return sanitizeDiagnosticText(trimmedValue);
}

function getMetadataBoolean(
  metadata: Record<string, unknown> | null,
  key: string,
): boolean | null {
  const value = metadata?.[key];
  return typeof value === "boolean" ? value : null;
}

function getTargetSummary(metadata: Record<string, unknown> | null): string | null {
  const target = asRecord(metadata?.target);
  const targetType = getMetadataString(target, "type");
  const targetId = getMetadataString(target, "id");
  if (!targetType || !targetId) {
    return null;
  }

  return `${targetType}:${targetId}`;
}

function getReferenceRoleCounts(
  sources: Array<Record<string, unknown>>,
): Array<{ count: number; label: string; role: string }> {
  for (const source of sources) {
    const roles = asRecord(source.reference_roles);
    if (!roles) {
      continue;
    }
    return Object.entries(roles)
      .map(([role, assetIds]) => ({
        count: Array.isArray(assetIds) ? assetIds.length : 0,
        label: referenceRoleLabel(role),
        role,
      }))
      .filter((entry) => entry.count > 0);
  }
  return [];
}

function getReferenceUsageItemCount(sources: Array<Record<string, unknown>>): number {
  for (const source of sources) {
    const usage = source.reference_usage;
    if (Array.isArray(usage)) {
      return usage.length;
    }
    const usageRecord = asRecord(usage);
    if (Array.isArray(usageRecord?.items)) {
      return usageRecord.items.length;
    }
  }
  return 0;
}

function getStringArrayFromSources(
  sources: Array<Record<string, unknown>>,
  key: string,
): string[] {
  for (const source of sources) {
    const value = source[key];
    if (!Array.isArray(value)) {
      continue;
    }
    return value
      .filter((item): item is string => typeof item === "string")
      .map(sanitizeDiagnosticText);
  }
  return [];
}

function getNumberFromSources(
  sources: Array<Record<string, unknown>>,
  key: string,
): number | null {
  for (const source of sources) {
    const value = source[key];
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
  }
  return null;
}

function referenceRoleLabel(role: string): string {
  return REFERENCE_ROLE_OPTIONS.find((option) => option.value === role)?.label ?? role;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }

  return value as Record<string, unknown>;
}

function sanitizeDiagnosticText(value: string): string {
  return value
    .replace(/[A-Z]:\\[^\s]+/g, "[local path redacted]")
    .replace(/api[_-]?key[^\s]*/gi, "[api key redacted]")
    .replace(/secret[^\s]*/gi, "[secret redacted]")
    .replace(/bearer\s+[^\s]+/gi, "Bearer [token redacted]");
}
