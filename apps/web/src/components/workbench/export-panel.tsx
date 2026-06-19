import type {
  ArtifactResponse,
  DesignVersionResponse,
  ExportResponse,
} from "@caragent/contracts";
import { AlertTriangle, CheckCircle2, Download, FileArchive, FileJson } from "lucide-react";

import { Button } from "@/components/ui/button";

type ConceptExportFormat = "png" | "jpg" | "enhanced_concept_handoff_zip";

interface ExportPanelProps {
  artifact: ArtifactResponse | null;
  artifacts: ArtifactResponse[];
  enhancedHandoffEnabled: boolean;
  error: string | null;
  exports: ExportResponse[];
  format: ConceptExportFormat;
  isSubmitting: boolean;
  notice: string | null;
  onFormatChange: (value: ConceptExportFormat) => void;
  onSubmit: () => void;
  selectedVersion: DesignVersionResponse | null;
}

const formatOptions: Array<{ label: string; value: ConceptExportFormat }> = [
  { label: "PNG", value: "png" },
  { label: "JPG", value: "jpg" },
  { label: "ZIP", value: "enhanced_concept_handoff_zip" },
];

const manifestDisclaimer = "概念预览，不是生产印刷文件。";
const handoffPackageDisclaimer = "概念交接包，仅供评审";
const missingRightsSourceText = "缺少版权或来源信息";

export function ExportPanel({
  artifact,
  artifacts,
  enhancedHandoffEnabled,
  error,
  exports,
  format,
  isSubmitting,
  notice,
  onFormatChange,
  onSubmit,
  selectedVersion,
}: ExportPanelProps) {
  const selectedExports = selectedVersion
    ? exports.filter((entry) => entry.version_id === selectedVersion.id)
    : [];
  const isHandoffPackage = format === "enhanced_concept_handoff_zip";
  const baseCanSubmit = selectedVersion !== null && artifact !== null && !isSubmitting;
  const objectKeyPreview = artifact ? summarizeObjectKey(artifact.object_key) : "-";
  const selectedPreviewSpec = readPreviewSpecSummary(selectedVersion?.parameters.preview_spec);
  const packageReadiness = readPackageReadiness({
    artifact,
    artifacts,
    selectedPreviewSpec,
    selectedVersion,
  });
  const hasPackageBlocker = packageReadiness.some((row) => row.state === "blocked");
  const hasRightsSourceBlocker = packageReadiness.some(
    (row) => row.value === missingRightsSourceText,
  );
  const canSubmit =
    baseCanSubmit && (!isHandoffPackage || (enhancedHandoffEnabled && !hasPackageBlocker));

  return (
    <form
      className="grid gap-3 rounded-md border border-border bg-background p-3"
      onSubmit={(event) => {
        event.preventDefault();
        if (canSubmit) {
          onSubmit();
        }
      }}
    >
      <div className="flex items-center gap-2">
        <Download aria-hidden="true" className="h-4 w-4 text-primary" />
        <div className="min-w-0">
          <p className="text-sm font-semibold">概念导出</p>
          <p className="truncate text-xs text-secondary-foreground">
            版本: {selectedVersion?.title ?? "未选择版本"}
          </p>
        </div>
      </div>

      <p className="rounded-md border border-dashed border-border bg-muted px-3 py-2 text-xs text-secondary-foreground">
        {isHandoffPackage ? handoffPackageDisclaimer : manifestDisclaimer}
      </p>

      <div className="grid gap-2">
        <p className="text-xs font-medium text-secondary-foreground">导出格式</p>
        <div className="grid grid-cols-3 gap-1">
          {formatOptions.map((option) => (
            <Button
              aria-pressed={format === option.value}
              disabled={
                !baseCanSubmit ||
                (option.value === "enhanced_concept_handoff_zip" &&
                  !enhancedHandoffEnabled)
              }
              key={option.value}
              onClick={() => {
                onFormatChange(option.value);
              }}
              size="sm"
              type="button"
              variant={format === option.value ? "default" : "outline"}
            >
              {option.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-2 rounded-md border border-border bg-card px-3 py-2 text-xs">
        <div className="flex items-center gap-2 font-medium">
          {isHandoffPackage ? (
            <FileArchive aria-hidden="true" className="h-3.5 w-3.5 text-primary" />
          ) : (
            <FileJson aria-hidden="true" className="h-3.5 w-3.5 text-primary" />
          )}
          {isHandoffPackage ? "交接包预览" : "Manifest 预览"}
        </div>
        <dl className="grid gap-1 text-secondary-foreground">
          <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
            <dt>版本</dt>
            <dd className="break-all">{selectedVersion?.id ?? "-"}</dd>
          </div>
          <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
            <dt>素材 ID</dt>
            <dd className="break-all">{artifact?.id ?? "-"}</dd>
          </div>
          <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
            <dt>对象键</dt>
            <dd className="break-all" title={artifact?.object_key}>
              {objectKeyPreview}
            </dd>
          </div>
          <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
            <dt>格式</dt>
            <dd>{format}</dd>
          </div>
        </dl>
        {selectedPreviewSpec ? <PreviewSpecSummary summary={selectedPreviewSpec} /> : null}
        {isHandoffPackage ? (
          <PackageReadinessRows rows={packageReadiness} />
        ) : null}
      </div>

      {isHandoffPackage && hasRightsSourceBlocker ? (
        <p className="text-xs font-medium text-destructive">{missingRightsSourceText}</p>
      ) : null}
      {notice ? <p className="text-xs text-primary">{notice}</p> : null}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}

      <Button disabled={!canSubmit} type="submit">
        {isSubmitting ? "创建中" : isHandoffPackage ? "生成交接包" : "创建概念导出"}
      </Button>

      <div className="grid gap-2 text-sm">
        <p className="text-xs font-medium text-secondary-foreground">导出历史</p>
        {selectedExports.length > 0 ? (
          selectedExports.map((entry) => (
            <div className="rounded-md border border-border bg-card px-3 py-2" key={entry.id}>
              <div className="flex flex-wrap gap-2 text-xs text-secondary-foreground">
                <span>{displayExportFormat(entry.format)}</span>
                <span>{entry.status}</span>
                <span>{entry.concept_label}</span>
              </div>
              <p className="mt-1 break-all text-xs text-secondary-foreground">
                {packageArtifactObjectKey(entry.manifest) ??
                  stringManifestValue(entry.manifest, "source_artifact_object_key") ??
                  stringManifestValue(entry.manifest, "source_artifact") ??
                  entry.artifact_id ??
                  "-"}
              </p>
              {stringManifestValue(entry.manifest, "disclaimer") ? (
                <p className="mt-1 text-xs">
                  {stringManifestValue(entry.manifest, "disclaimer")}
                </p>
              ) : null}
              <ExportPackageFiles manifest={entry.manifest} />
              <ExportManifestPreviewSpec manifest={entry.manifest} />
            </div>
          ))
        ) : (
          <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-secondary-foreground">
            暂无导出
          </p>
        )}
      </div>
    </form>
  );
}

interface PackageReadinessRow {
  label: string;
  state: "blocked" | "ready" | "warning";
  value: string;
}

function PackageReadinessRows({ rows }: { rows: PackageReadinessRow[] }) {
  return (
    <div className="mt-2 grid gap-1 text-xs">
      {rows.map((row) => (
        <div
          className="grid grid-cols-[16px_minmax(0,1fr)] items-center gap-2 text-secondary-foreground"
          key={row.label}
        >
          {row.state === "ready" ? (
            <CheckCircle2 aria-hidden="true" className="h-3.5 w-3.5 text-primary" />
          ) : (
            <AlertTriangle
              aria-hidden="true"
              className={
                row.state === "blocked"
                  ? "h-3.5 w-3.5 text-destructive"
                  : "h-3.5 w-3.5 text-warning"
              }
            />
          )}
          <span
            className={
              row.state === "blocked" ? "truncate text-destructive" : "truncate"
            }
          >
            {row.label} {row.value}
          </span>
        </div>
      ))}
    </div>
  );
}

interface PreviewSpecSummaryData {
  overlayLayerCount: number;
  safeZoneCount: number;
  warningCount: number;
}

function PreviewSpecSummary({ summary }: { summary: PreviewSpecSummaryData }) {
  return (
    <div className="mt-2 grid gap-2 rounded-md border border-border bg-muted px-3 py-2 text-xs">
      <p className="font-medium text-foreground">PreviewSpec 摘要</p>
      <div className="flex flex-wrap gap-2 text-secondary-foreground">
        <span>图层 {summary.overlayLayerCount}</span>
        <span>安全区 {summary.safeZoneCount}</span>
        <span>警告 {summary.warningCount}</span>
      </div>
    </div>
  );
}

function ExportManifestPreviewSpec({ manifest }: { manifest: ExportResponse["manifest"] }) {
  const summary = readPreviewSpecSummaryFromManifest(manifest);
  return summary ? <PreviewSpecSummary summary={summary} /> : null;
}

function ExportPackageFiles({ manifest }: { manifest: ExportResponse["manifest"] }) {
  const files = Array.isArray(manifest.files) ? manifest.files : [];
  const paths = files
    .map((item) => (isRecord(item) && typeof item.path === "string" ? item.path : null))
    .filter((path): path is string => path !== null);
  if (paths.length === 0) {
    return null;
  }
  return (
    <div className="mt-2 flex flex-wrap gap-1 text-xs text-secondary-foreground">
      {paths.slice(0, 4).map((path) => (
        <span className="rounded-sm border border-border px-1.5 py-0.5" key={path}>
          {path}
        </span>
      ))}
    </div>
  );
}

function readPreviewSpecSummaryFromManifest(
  manifest: ExportResponse["manifest"],
): PreviewSpecSummaryData | null {
  const parameters = manifest.parameters;
  if (!isRecord(parameters)) {
    return null;
  }
  return readPreviewSpecSummary(parameters.preview_spec);
}

function readPreviewSpecSummary(value: unknown): PreviewSpecSummaryData | null {
  if (!isRecord(value)) {
    return null;
  }

  return {
    overlayLayerCount: readArrayLength(value.overlay_layers),
    safeZoneCount: readArrayLength(value.safe_zones),
    warningCount: readArrayLength(value.warnings),
  };
}

function readPackageReadiness({
  artifact,
  artifacts,
  selectedPreviewSpec,
  selectedVersion,
}: {
  artifact: ArtifactResponse | null;
  artifacts: ArtifactResponse[];
  selectedPreviewSpec: PreviewSpecSummaryData | null;
  selectedVersion: DesignVersionResponse | null;
}): PackageReadinessRow[] {
  const parameters = selectedVersion?.parameters ?? {};
  const screenshotCount =
    selectedVersion === null
      ? 0
      : artifacts.filter(
          (entry) =>
            entry.version_id === selectedVersion.id && entry.kind === "preview_3d_screenshot",
        ).length;
  const referenceCount = readArrayLength(parameters.included_reference_asset_ids);
  const hasRightsSourceBlocker = hasHandoffRightsSourceBlocker(parameters);
  return [
    {
      label: "概念图",
      state: artifact !== null ? "ready" : "blocked",
      value: artifact ? "已选择" : "缺失",
    },
    {
      label: "3D 截图",
      state: screenshotCount > 0 ? "ready" : "warning",
      value: screenshotCount > 0 ? `${screenshotCount}` : "未包含 3D 截图",
    },
    {
      label: "安全区/警告",
      state: selectedPreviewSpec !== null ? "ready" : "warning",
      value: selectedPreviewSpec
        ? `${selectedPreviewSpec.safeZoneCount}/${selectedPreviewSpec.warningCount}`
        : "缺失",
    },
    {
      label: "Prompt/Provider",
      state:
        selectedVersion?.job_id !== null && selectedVersion?.job_id !== undefined
          ? "ready"
          : "warning",
      value: selectedVersion?.job_id ? "已关联" : "缺失",
    },
    {
      label: "参考素材",
      state: hasRightsSourceBlocker ? "blocked" : referenceCount > 0 ? "ready" : "warning",
      value: hasRightsSourceBlocker ? missingRightsSourceText : `${referenceCount}`,
    },
    {
      label: "评审备注",
      state: "ready",
      value: "可选",
    },
  ];
}

function hasHandoffRightsSourceBlocker(parameters: Record<string, unknown>): boolean {
  const includedReferenceAssetIds = readStringArray(parameters.included_reference_asset_ids);
  if (includedReferenceAssetIds.length === 0) {
    return false;
  }
  const rightsSnapshot = isRecord(parameters.rights_snapshot)
    ? parameters.rights_snapshot
    : {};

  return includedReferenceAssetIds.some((assetId) => {
    const snapshot = rightsSnapshot[assetId];
    if (!isRecord(snapshot)) {
      return true;
    }
    const rightsStatus = stringRecordValue(snapshot, "rights_status").toLowerCase();
    const sourceLabel = stringRecordValue(snapshot, "source_label");
    const sourceUrl = stringRecordValue(snapshot, "source_url");
    return rightsStatus !== "confirmed" || (sourceLabel === "" && sourceUrl === "");
  });
}

function readArrayLength(value: unknown): number {
  return Array.isArray(value) ? value.length : 0;
}

function readStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => (typeof item === "string" ? item.trim() : ""))
    .filter((item) => item.length > 0);
}

function stringRecordValue(record: Record<string, unknown>, key: string): string {
  const value = record[key];
  return typeof value === "string" ? value.trim() : "";
}

function stringManifestValue(
  manifest: ExportResponse["manifest"],
  key: string,
): string | null {
  const value = manifest[key];
  return typeof value === "string" ? value : null;
}

function packageArtifactObjectKey(manifest: ExportResponse["manifest"]): string | null {
  const packageArtifact = manifest.package_artifact;
  if (!isRecord(packageArtifact)) {
    return null;
  }
  return typeof packageArtifact.object_key === "string" ? packageArtifact.object_key : null;
}

function displayExportFormat(format: string): string {
  return format === "enhanced_concept_handoff_zip" ? "ZIP" : format.toUpperCase();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function summarizeObjectKey(objectKey: string): string {
  const parts = objectKey.split("/");
  if (parts.length <= 1) {
    return objectKey;
  }

  return [...parts.slice(0, -1), "..."].join("/");
}

export { handoffPackageDisclaimer, manifestDisclaimer };
export type { ConceptExportFormat };
