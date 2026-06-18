import type {
  ArtifactResponse,
  DesignVersionResponse,
  ExportResponse,
} from "@caragent/contracts";
import { Download, FileJson } from "lucide-react";

import { Button } from "@/components/ui/button";

type ConceptExportFormat = "png" | "jpg";

interface ExportPanelProps {
  artifact: ArtifactResponse | null;
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
];

const manifestDisclaimer = "概念预览，不是生产印刷文件。";

export function ExportPanel({
  artifact,
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
  const canSubmit = selectedVersion !== null && artifact !== null && !isSubmitting;
  const objectKeyPreview = artifact ? summarizeObjectKey(artifact.object_key) : "-";
  const selectedPreviewSpec = readPreviewSpecSummary(selectedVersion?.parameters.preview_spec);

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
        {manifestDisclaimer}
      </p>

      <div className="grid gap-2">
        <p className="text-xs font-medium text-secondary-foreground">导出格式</p>
        <div className="grid grid-cols-2 gap-1">
          {formatOptions.map((option) => (
            <Button
              aria-pressed={format === option.value}
              disabled={!canSubmit}
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
          <FileJson aria-hidden="true" className="h-3.5 w-3.5 text-primary" />
          Manifest 预览
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
      </div>

      {notice ? <p className="text-xs text-primary">{notice}</p> : null}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}

      <Button disabled={!canSubmit} type="submit">
        {isSubmitting ? "创建中" : "创建概念导出"}
      </Button>

      <div className="grid gap-2 text-sm">
        <p className="text-xs font-medium text-secondary-foreground">导出历史</p>
        {selectedExports.length > 0 ? (
          selectedExports.map((entry) => (
            <div className="rounded-md border border-border bg-card px-3 py-2" key={entry.id}>
              <div className="flex flex-wrap gap-2 text-xs text-secondary-foreground">
                <span>{entry.format.toUpperCase()}</span>
                <span>{entry.status}</span>
                <span>{entry.concept_label}</span>
              </div>
              <p className="mt-1 break-all text-xs text-secondary-foreground">
                {stringManifestValue(entry.manifest, "source_artifact_object_key") ??
                  stringManifestValue(entry.manifest, "source_artifact") ??
                  entry.artifact_id ??
                  "-"}
              </p>
              {stringManifestValue(entry.manifest, "disclaimer") ? (
                <p className="mt-1 text-xs">
                  {stringManifestValue(entry.manifest, "disclaimer")}
                </p>
              ) : null}
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

function readArrayLength(value: unknown): number {
  return Array.isArray(value) ? value.length : 0;
}

function stringManifestValue(
  manifest: ExportResponse["manifest"],
  key: string,
): string | null {
  const value = manifest[key];
  return typeof value === "string" ? value : null;
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

export { manifestDisclaimer };
export type { ConceptExportFormat };
