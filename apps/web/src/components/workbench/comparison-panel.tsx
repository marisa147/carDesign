import type { DesignVersionResponse } from "@caragent/contracts";

import { Badge } from "@/components/ui/badge";
import { useWorkbenchStore } from "@/lib/workbench/store";

interface ComparisonPanelProps {
  versions: DesignVersionResponse[];
}

export function ComparisonPanel({ versions }: ComparisonPanelProps) {
  const selectedVersionId = useWorkbenchStore((state) => state.selectedVersionId);
  const selectedVersion = selectVersion(versions, selectedVersionId);
  const parentVersion = selectedVersion?.parent_version_id
    ? versions.find((version) => version.id === selectedVersion.parent_version_id) ?? null
    : null;
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
          <p className="text-sm font-semibold">版本对比</p>
          <p className="mt-1 text-xs text-secondary-foreground">
            谱系深度 {selectedVersion.lineage_depth}
          </p>
        </div>
        <Badge variant="muted">仅对比元数据和参数</Badge>
      </div>

      <div className="grid gap-1 text-sm">
        <p>父版本: {parentVersion?.title ?? "无"}</p>
        <p>当前版本: {selectedVersion.title ?? selectedVersion.id}</p>
      </div>

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

function selectVersion(
  versions: DesignVersionResponse[],
  selectedVersionId: string | null,
): DesignVersionResponse | null {
  return versions.find((version) => version.id === selectedVersionId) ?? versions[0] ?? null;
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
