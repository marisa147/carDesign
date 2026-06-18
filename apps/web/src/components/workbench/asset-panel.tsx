"use client";

import type { AssetResponse, AssetRightsUpdateRequest, ReferenceRole } from "@caragent/contracts";
import { AlertTriangle, CheckCircle2, Loader2, Upload } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getReferenceEligibility } from "@/lib/api/assets";
import {
  DEFAULT_REFERENCE_ROLE,
  REFERENCE_ROLE_OPTIONS,
  type ReferenceUsageDraft,
} from "@/lib/api/generation";

interface AssetPanelProps {
  assets: AssetResponse[];
  isLoading: boolean;
  onReferenceAssignmentChange: (
    assetId: string,
    changes: { enabled?: boolean; role?: ReferenceRole },
  ) => void;
  onRightsUpdate: (
    assetId: string,
    payload: AssetRightsUpdateRequest,
  ) => Promise<AssetResponse>;
  onUpload: (payload: { file: File; kind: string }) => Promise<AssetResponse>;
  referenceAssignments: ReferenceUsageDraft[];
  workspaceId: string | null;
}

export function AssetPanel({
  assets,
  isLoading,
  onReferenceAssignmentChange,
  onRightsUpdate,
  onUpload,
  referenceAssignments,
  workspaceId,
}: AssetPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [kind, setKind] = useState("reference");
  const [uploadState, setUploadState] = useState<"idle" | "uploading" | "error">(
    "idle",
  );

  const canUpload = workspaceId !== null && file !== null && uploadState !== "uploading";

  const handleUpload = async () => {
    if (!file || !canUpload) {
      return;
    }

    setUploadState("uploading");
    try {
      await onUpload({ file, kind });
      setFile(null);
      setUploadState("idle");
    } catch {
      setUploadState("error");
    }
  };

  return (
    <div className="grid gap-3 text-sm">
      <div className="grid gap-2">
        <label className="text-xs font-medium text-secondary-foreground" htmlFor="asset-file">
          上传素材文件
        </label>
        <input
          accept="image/*"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-muted file:px-3 file:py-1.5 file:text-xs file:font-medium"
          id="asset-file"
          onChange={(event) => {
            setFile(event.target.files?.[0] ?? null);
            setUploadState("idle");
          }}
          type="file"
        />
        <label className="text-xs font-medium text-secondary-foreground" htmlFor="asset-kind">
          素材类型
        </label>
        <select
          className="h-9 rounded-md border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
          id="asset-kind"
          onChange={(event) => {
            setKind(event.target.value);
          }}
          value={kind}
        >
          <option value="reference">参考图</option>
          <option value="logo">Logo</option>
          <option value="vehicle">车辆照片</option>
        </select>
        <Button disabled={!canUpload} onClick={handleUpload} type="button" variant="outline">
          {uploadState === "uploading" ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <Upload aria-hidden="true" className="h-4 w-4" />
          )}
          上传素材
        </Button>
        {workspaceId === null ? (
          <p className="text-xs text-secondary-foreground">先发送设计需求以创建工作台。</p>
        ) : null}
        {uploadState === "error" ? (
          <p className="text-xs text-destructive" role="alert">
            素材上传失败。请确认 API 和对象存储已启动后重试。
          </p>
        ) : null}
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2 text-secondary-foreground">
          <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin text-primary" />
          正在加载素材
        </div>
      ) : null}

      {assets.length === 0 ? (
        <p className="rounded-md border border-dashed border-border bg-muted px-3 py-3 text-secondary-foreground">
          上传参考图、Logo 或车辆照片，并补充来源/权利信息后再用于生成。
        </p>
      ) : (
        <div className="grid gap-3">
          {assets.map((asset) => (
            <AssetListItem
              asset={asset}
              assignment={referenceAssignments.find(
                (referenceAssignment) => referenceAssignment.assetId === asset.id,
              )}
              key={`${asset.id}-${asset.updated_at}`}
              onReferenceAssignmentChange={onReferenceAssignmentChange}
              onRightsUpdate={onRightsUpdate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function AssetListItem({
  assignment,
  asset,
  onReferenceAssignmentChange,
  onRightsUpdate,
}: {
  assignment: ReferenceUsageDraft | undefined;
  asset: AssetResponse;
  onReferenceAssignmentChange: (
    assetId: string,
    changes: { enabled?: boolean; role?: ReferenceRole },
  ) => void;
  onRightsUpdate: (
    assetId: string,
    payload: AssetRightsUpdateRequest,
  ) => Promise<AssetResponse>;
}) {
  const [sourceLabel, setSourceLabel] = useState(asset.source_label ?? "");
  const [rightsNotes, setRightsNotes] = useState(asset.rights_notes ?? "");
  const [saveState, setSaveState] = useState<"idle" | "saving" | "error">("idle");
  const isConfirmed = asset.rights_status === "confirmed";
  const eligibility = getReferenceEligibility(asset);
  const selectedRole = assignment?.role ?? DEFAULT_REFERENCE_ROLE;
  const isSelected = Boolean(assignment?.enabled);

  const handleRightsSave = async () => {
    setSaveState("saving");
    try {
      await onRightsUpdate(asset.id, {
        rights_notes: rightsNotes.trim() || null,
        rights_status: "confirmed",
        source_label: sourceLabel.trim() || null,
        source_url: null,
      });
      setSaveState("idle");
    } catch {
      setSaveState("error");
    }
  };

  return (
    <div className="grid gap-3 rounded-md border border-border bg-muted p-3">
      <div className="flex min-w-0 items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate font-medium">{asset.original_filename}</p>
          <p className="text-xs text-secondary-foreground">
            {asset.kind} · {asset.content_type} · {asset.byte_size} bytes
          </p>
        </div>
        <RightsBadge isConfirmed={isConfirmed} />
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input
          checked={isSelected}
          disabled={!eligibility.canUseForGeneration}
          onChange={(event) => {
            onReferenceAssignmentChange(asset.id, { enabled: event.target.checked });
          }}
          type="checkbox"
        />
        用于生成 {asset.original_filename}
      </label>
      <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
        <div>
          <label
            className="text-xs font-medium text-secondary-foreground"
            htmlFor={`reference-role-${asset.id}`}
          >
            引用角色 {asset.original_filename}
          </label>
          <select
            className="mt-1 h-9 w-full rounded-md border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
            id={`reference-role-${asset.id}`}
            onChange={(event) => {
              onReferenceAssignmentChange(asset.id, {
                role: event.target.value as ReferenceRole,
              });
            }}
            value={selectedRole}
          >
            {REFERENCE_ROLE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant={eligibility.canUseForGeneration ? "primary" : "warning"}>
            {eligibility.label}
          </Badge>
          {eligibility.warning ? <Badge variant="warning">{eligibility.warning}</Badge> : null}
        </div>
      </div>

      <div className="grid gap-2">
        <label className="text-xs font-medium text-secondary-foreground" htmlFor={`source-${asset.id}`}>
          素材来源 {asset.original_filename}
        </label>
        <input
          className="h-9 rounded-md border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
          id={`source-${asset.id}`}
          onChange={(event) => {
            setSourceLabel(event.target.value);
          }}
          value={sourceLabel}
        />
        <label className="text-xs font-medium text-secondary-foreground" htmlFor={`rights-${asset.id}`}>
          权利备注 {asset.original_filename}
        </label>
        <textarea
          className="min-h-16 rounded-md border border-input bg-background px-3 py-2 text-sm leading-6 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-ring"
          id={`rights-${asset.id}`}
          onChange={(event) => {
            setRightsNotes(event.target.value);
          }}
          value={rightsNotes}
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button
          disabled={saveState === "saving"}
          onClick={handleRightsSave}
          type="button"
          variant="outline"
        >
          {saveState === "saving" ? (
            <Loader2 aria-hidden="true" className="h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
          )}
          确认权利 {asset.original_filename}
        </Button>
        {saveState === "error" ? (
          <span className="inline-flex items-center gap-1 text-xs text-destructive" role="alert">
            <AlertTriangle aria-hidden="true" className="h-4 w-4" />
            权利保存失败
          </span>
        ) : null}
      </div>
    </div>
  );
}

function RightsBadge({ isConfirmed }: { isConfirmed: boolean }) {
  if (isConfirmed) {
    return <Badge variant="primary">权利已确认</Badge>;
  }

  return <Badge variant="warning">权利信息缺失</Badge>;
}
