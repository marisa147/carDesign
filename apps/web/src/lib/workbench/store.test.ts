import { afterEach, describe, expect, it } from "vitest";

import { workbenchQueryKeys } from "@/lib/workbench/query-keys";
import { useWorkbenchStore } from "@/lib/workbench/store";

describe("workbench state boundaries", () => {
  afterEach(() => {
    useWorkbenchStore.getState().resetWorkbenchUi();
  });

  it("builds stable query keys for canonical server state", () => {
    expect(workbenchQueryKeys.workspace("workspace-1")).toEqual([
      "workspace",
      "workspace-1",
    ]);
    expect(workbenchQueryKeys.messages("workspace-1")).toEqual([
      "messages",
      "workspace-1",
    ]);
    expect(workbenchQueryKeys.briefs("workspace-1")).toEqual([
      "briefs",
      "workspace-1",
    ]);
    expect(workbenchQueryKeys.assets("workspace-1")).toEqual([
      "assets",
      "workspace-1",
    ]);
    expect(workbenchQueryKeys.generationState("workspace-1", "job-1")).toEqual([
      "generation-state",
      "workspace-1",
      "job-1",
    ]);
    expect(workbenchQueryKeys.feedback("workspace-1")).toEqual([
      "feedback",
      "workspace-1",
    ]);
    expect(workbenchQueryKeys.exports("workspace-1")).toEqual([
      "exports",
      "workspace-1",
    ]);
    expect(workbenchQueryKeys.iteration("workspace-1", "version-1")).toEqual([
      "iteration",
      "workspace-1",
      "version-1",
    ]);
  });

  it("keeps only synchronous UI state in the local store", () => {
    const state = useWorkbenchStore.getState();

    expect(Object.keys(state)).not.toContain("messages");
    expect(Object.keys(state)).not.toContain("jobs");
    expect(Object.keys(state)).not.toContain("assets");
    expect(Object.keys(state)).not.toContain("briefs");

    state.setSelectedVersionId("version-1");
    state.setSelectedView("front");
    state.setPreviewZoom(1.5);
    state.panPreview({ x: 24, y: -12 });

    expect(useWorkbenchStore.getState()).toMatchObject({
      previewPan: { x: 24, y: -12 },
      previewZoom: 1.5,
      selectedVersionId: "version-1",
      selectedView: "front",
    });
  });

  it("resets preview transform without clearing selected context", () => {
    useWorkbenchStore.getState().setSelectedVersionId("version-1");
    useWorkbenchStore.getState().setSelectedView("rear");
    useWorkbenchStore.getState().setPreviewZoom(2);
    useWorkbenchStore.getState().panPreview({ x: 32, y: 16 });

    useWorkbenchStore.getState().resetPreviewTransform();

    expect(useWorkbenchStore.getState()).toMatchObject({
      previewPan: { x: 0, y: 0 },
      previewZoom: 1,
      selectedVersionId: "version-1",
      selectedView: "rear",
    });
  });

  it("steps preview zoom through clamped local controls", () => {
    const state = useWorkbenchStore.getState();

    state.zoomPreviewIn();
    state.zoomPreviewIn();

    expect(useWorkbenchStore.getState().previewZoom).toBe(1.5);

    state.zoomPreviewOut();

    expect(useWorkbenchStore.getState().previewZoom).toBe(1.25);

    state.resetPreviewTransform();

    expect(useWorkbenchStore.getState().previewZoom).toBe(1);
  });

  it("toggles PreviewSpec overlays locally and resets them with the workbench UI", () => {
    const state = useWorkbenchStore.getState();

    expect(state.showOverlayLayers).toBe(true);
    expect(state.showSafeZones).toBe(false);

    state.setSelectedVersionId("version-1");
    state.toggleOverlayLayers();
    state.toggleSafeZones();

    expect(useWorkbenchStore.getState()).toMatchObject({
      selectedVersionId: "version-1",
      showOverlayLayers: false,
      showSafeZones: true,
    });

    useWorkbenchStore.getState().resetWorkbenchUi();

    expect(useWorkbenchStore.getState()).toMatchObject({
      selectedVersionId: null,
      showOverlayLayers: true,
      showSafeZones: false,
    });
  });
});
