import { create } from "zustand";

export type WorkbenchView = "front" | "rear" | "side" | "top";
export type WorkbenchTab = "assets" | "history" | "parameters";

export interface PreviewPan {
  x: number;
  y: number;
}

interface WorkbenchUiState {
  activeInspectorTab: WorkbenchTab;
  previewPan: PreviewPan;
  previewZoom: number;
  selectedVersionId: string | null;
  selectedView: WorkbenchView;
  showOverlayLayers: boolean;
  showSafeZones: boolean;
  panPreview: (pan: PreviewPan) => void;
  resetPreviewTransform: () => void;
  resetWorkbenchUi: () => void;
  setActiveInspectorTab: (tab: WorkbenchTab) => void;
  setPreviewZoom: (zoom: number) => void;
  setSelectedVersionId: (versionId: string | null) => void;
  setSelectedView: (view: WorkbenchView) => void;
  toggleOverlayLayers: () => void;
  toggleSafeZones: () => void;
  zoomPreviewIn: () => void;
  zoomPreviewOut: () => void;
}

const initialWorkbenchUiState = {
  activeInspectorTab: "parameters" as WorkbenchTab,
  previewPan: { x: 0, y: 0 },
  previewZoom: 1,
  selectedVersionId: null,
  selectedView: "side" as WorkbenchView,
  showOverlayLayers: true,
  showSafeZones: false,
};

const previewZoomStep = 0.25;
const minPreviewZoom = 0.5;
const maxPreviewZoom = 3;

export const useWorkbenchStore = create<WorkbenchUiState>()((set) => ({
  ...initialWorkbenchUiState,
  panPreview: (previewPan) => {
    set({ previewPan });
  },
  resetPreviewTransform: () => {
    set({
      previewPan: initialWorkbenchUiState.previewPan,
      previewZoom: initialWorkbenchUiState.previewZoom,
    });
  },
  resetWorkbenchUi: () => {
    set(initialWorkbenchUiState);
  },
  setActiveInspectorTab: (activeInspectorTab) => {
    set({ activeInspectorTab });
  },
  setPreviewZoom: (previewZoom) => {
    set({ previewZoom });
  },
  setSelectedVersionId: (selectedVersionId) => {
    set({ selectedVersionId });
  },
  setSelectedView: (selectedView) => {
    set({ selectedView });
  },
  toggleOverlayLayers: () => {
    set((state) => ({ showOverlayLayers: !state.showOverlayLayers }));
  },
  toggleSafeZones: () => {
    set((state) => ({ showSafeZones: !state.showSafeZones }));
  },
  zoomPreviewIn: () => {
    set((state) => ({
      previewZoom: clampZoom(state.previewZoom + previewZoomStep),
    }));
  },
  zoomPreviewOut: () => {
    set((state) => ({
      previewZoom: clampZoom(state.previewZoom - previewZoomStep),
    }));
  },
}));

function clampZoom(value: number): number {
  return Math.min(maxPreviewZoom, Math.max(minPreviewZoom, value));
}
