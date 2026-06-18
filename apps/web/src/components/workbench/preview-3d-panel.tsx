"use client";

import type { ArtifactResponse, DesignVersionResponse } from "@caragent/contracts";
import { Camera, Minus, Plus, RotateCcw, RotateCw } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  PREVIEW_3D_FALLBACK_MESSAGE,
  buildPreview3DCompatibility,
} from "@/lib/preview3d/spec";
import { useWorkbenchStore } from "@/lib/workbench/store";

import { Preview3DViewer } from "./preview-3d-viewer";

interface Preview3DPanelProps {
  artifact: ArtifactResponse | null;
  version: DesignVersionResponse;
}

export function Preview3DPanel({ artifact, version }: Preview3DPanelProps) {
  const [captureStatus, setCaptureStatus] = useState<string | null>(null);
  const {
    preview3DCamera,
    resetPreview3DCamera,
    rotatePreview3D,
    zoomPreview3DIn,
    zoomPreview3DOut,
  } = useWorkbenchStore();
  const compatibility = buildPreview3DCompatibility({ artifact, version });

  return (
    <div className="grid gap-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-lg font-semibold">概念 3D 预览</h3>
          <p className="mt-1 text-sm text-secondary-foreground">
            {version.summary ?? version.title ?? "Generated 3D concept preview."}
          </p>
        </div>
        <span className="rounded-md border border-border bg-background px-2 py-1 text-xs font-medium text-secondary-foreground">
          非生产贴膜参考
        </span>
      </div>

      {compatibility.status === "compatible" ? (
        <>
          <Preview3DViewer camera={preview3DCamera} compatibility={compatibility} />
          <div className="flex flex-wrap items-center gap-2">
            <Button
              aria-label="向左旋转"
              onClick={() => {
                rotatePreview3D(-15);
              }}
              size="sm"
              type="button"
              variant="outline"
            >
              <RotateCcw aria-hidden="true" className="h-4 w-4" />
            </Button>
            <Button
              aria-label="向右旋转"
              onClick={() => {
                rotatePreview3D(15);
              }}
              size="sm"
              type="button"
              variant="outline"
            >
              <RotateCw aria-hidden="true" className="h-4 w-4" />
            </Button>
            <Button
              aria-label="缩小 3D"
              onClick={zoomPreview3DOut}
              size="sm"
              type="button"
              variant="outline"
            >
              <Minus aria-hidden="true" className="h-4 w-4" />
            </Button>
            <span className="min-w-14 text-center text-sm font-medium">
              {Math.round(preview3DCamera.zoom * 100)}%
            </span>
            <Button
              aria-label="放大 3D"
              onClick={zoomPreview3DIn}
              size="sm"
              type="button"
              variant="outline"
            >
              <Plus aria-hidden="true" className="h-4 w-4" />
            </Button>
            <Button onClick={resetPreview3DCamera} size="sm" type="button" variant="outline">
              <RotateCcw aria-hidden="true" className="h-4 w-4" />
              重置相机
            </Button>
            <Button
              onClick={() => {
                setCaptureStatus("截图已准备，后续计划会保存为 3D 预览工件。");
              }}
              size="sm"
              type="button"
              variant="outline"
            >
              <Camera aria-hidden="true" className="h-4 w-4" />
              截图
            </Button>
          </div>
          <div className="grid gap-1 text-xs text-secondary-foreground">
            <p>Shell {compatibility.shell?.id}</p>
            <p>Camera {compatibility.cameraPresetId}</p>
            <p className="break-all">Source {compatibility.source.artifactObjectKey}</p>
          </div>
        </>
      ) : (
        <div className="grid min-h-64 place-items-center rounded-md border border-border bg-background p-6 text-center">
          <div>
            <p className="text-sm font-medium">{PREVIEW_3D_FALLBACK_MESSAGE}</p>
            {compatibility.reason ? (
              <p className="mt-2 text-xs text-secondary-foreground">{compatibility.reason}</p>
            ) : null}
            <p className="mt-3 text-xs text-secondary-foreground">
              2D 预览、生成、迭代和导出仍可继续使用。
            </p>
          </div>
        </div>
      )}

      {captureStatus ? (
        <p className="text-xs font-medium text-primary" role="status">
          {captureStatus}
        </p>
      ) : null}
    </div>
  );
}
