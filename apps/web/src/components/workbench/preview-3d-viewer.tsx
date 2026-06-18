"use client";

import type { Group, PerspectiveCamera, WebGLRenderer } from "three";
import { useEffect, useRef, useState, type CSSProperties } from "react";

import { cn } from "@/lib/utils";
import type { Preview3DCompatibilityResult } from "@/lib/preview3d/spec";
import type { Preview3DCamera } from "@/lib/workbench/store";

interface Preview3DViewerProps {
  camera: Preview3DCamera;
  compatibility: Preview3DCompatibilityResult;
}

type ViewerStatus = "loading" | "ready" | "fallback";

export function Preview3DViewer({ camera, compatibility }: Preview3DViewerProps) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [status, setStatus] = useState<ViewerStatus>("loading");

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount || compatibility.status !== "compatible") {
      const fallbackTimer = window.setTimeout(() => {
        setStatus("fallback");
      }, 0);
      return () => {
        window.clearTimeout(fallbackTimer);
      };
    }

    const probeCanvas = document.createElement("canvas");
    const webglContext =
      probeCanvas.getContext("webgl") ?? probeCanvas.getContext("experimental-webgl");
    if (!webglContext) {
      const fallbackTimer = window.setTimeout(() => {
        setStatus("fallback");
      }, 0);
      return () => {
        window.clearTimeout(fallbackTimer);
      };
    }

    let animationFrame: number | null = null;
    let disposed = false;
    let renderer: WebGLRenderer | null = null;
    let sceneCamera: PerspectiveCamera | null = null;
    let shellGroup: Group | null = null;
    let cleanupScene = () => {};

    async function createScene() {
      const THREE = await import("three");
      if (disposed || !mountRef.current) {
        return;
      }

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0xf8fafc);

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      mountRef.current.appendChild(renderer.domElement);

      sceneCamera = new THREE.PerspectiveCamera(42, 2, 0.1, 100);
      shellGroup = new THREE.Group();

      const bodyGeometry = new THREE.BoxGeometry(3.8, 0.72, 1.35);
      const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0xe5e7eb,
        metalness: 0.1,
        roughness: 0.72,
      });
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
      body.position.y = 0.55;
      shellGroup.add(body);

      const cabinGeometry = new THREE.BoxGeometry(1.65, 0.56, 1.05);
      const cabinMaterial = new THREE.MeshStandardMaterial({
        color: 0x94a3b8,
        metalness: 0.05,
        roughness: 0.62,
      });
      const cabin = new THREE.Mesh(cabinGeometry, cabinMaterial);
      cabin.position.set(-0.28, 1.08, 0);
      shellGroup.add(cabin);

      const decalGeometries: Array<{ dispose: () => void }> = [];
      const decalMaterials: Array<{ dispose: () => void }> = [];
      for (const zone of compatibility.materialPlan.safeZones) {
        const geometry = new THREE.PlaneGeometry(zone.bounds.width * 3.5, zone.bounds.height * 1.1);
        const material = new THREE.MeshBasicMaterial({
          color: 0x2563eb,
          opacity: 0.2,
          side: THREE.DoubleSide,
          transparent: true,
        });
        const marker = new THREE.Mesh(geometry, material);
        marker.position.set((zone.bounds.x - 0.5) * 3.5, 0.74 - zone.bounds.y * 0.9, 0.681);
        shellGroup.add(marker);
        decalGeometries.push(geometry);
        decalMaterials.push(material);
      }

      scene.add(shellGroup);
      scene.add(new THREE.AmbientLight(0xffffff, 0.75));
      const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
      keyLight.position.set(2.6, 3.2, 4);
      scene.add(keyLight);

      const renderFrame = () => {
        if (!renderer || !sceneCamera || !shellGroup || disposed || !mountRef.current) {
          return;
        }

        const { height, width } = mountRef.current.getBoundingClientRect();
        const canvasWidth = Math.max(320, Math.floor(width));
        const canvasHeight = Math.max(220, Math.floor(height));
        renderer.setSize(canvasWidth, canvasHeight, false);
        sceneCamera.aspect = canvasWidth / canvasHeight;
        sceneCamera.updateProjectionMatrix();

        const radians = (camera.rotationY * Math.PI) / 180;
        const distance = 5 / camera.zoom;
        sceneCamera.position.set(Math.sin(radians) * distance, 1.7, Math.cos(radians) * distance);
        sceneCamera.lookAt(0, 0.7, 0);
        shellGroup.rotation.y = radians * 0.18;
        renderer.render(scene, sceneCamera);

        if (!prefersReducedMotion()) {
          animationFrame = window.requestAnimationFrame(renderFrame);
        }
      };

      renderFrame();
      setStatus("ready");

      cleanupScene = () => {
        if (animationFrame !== null) {
          window.cancelAnimationFrame(animationFrame);
        }
        bodyGeometry.dispose();
        bodyMaterial.dispose();
        cabinGeometry.dispose();
        cabinMaterial.dispose();
        for (const geometry of decalGeometries) {
          geometry.dispose();
        }
        for (const material of decalMaterials) {
          material.dispose();
        }
        renderer?.dispose();
        renderer?.domElement.remove();
      };
    }

    void createScene();

    return () => {
      disposed = true;
      cleanupScene();
    };
  }, [camera.rotationY, camera.zoom, compatibility.materialPlan.safeZones, compatibility.status]);

  return (
    <div
      aria-label={`3D preview surface for ${
        compatibility.shell?.label ?? "unsupported shell"
      }`}
      className="relative min-h-64 overflow-hidden rounded-md border border-border bg-background"
      ref={mountRef}
    >
      {status !== "ready" ? (
        <div
          className="absolute inset-0 grid place-items-center bg-muted p-4"
          role="img"
          style={{
            transform: `scale(${camera.zoom})`,
            transformOrigin: "center",
          }}
        >
          <div
            className={cn(
              "relative h-28 w-64 max-w-full rounded-[24px] border-2 border-foreground bg-card shadow-sm",
              status === "loading" ? "opacity-80" : "opacity-100",
            )}
            style={{ transform: `rotateY(${camera.rotationY}deg)` }}
          >
            <div className="absolute left-[24%] top-[-28%] h-[42%] w-[42%] rounded-t-md border-2 border-foreground bg-background" />
            <div className="absolute bottom-[-18%] left-[18%] h-11 w-11 rounded-full bg-foreground" />
            <div className="absolute bottom-[-18%] right-[18%] h-11 w-11 rounded-full bg-foreground" />
            <div className="absolute left-[28%] top-[34%] h-[30%] w-[38%] rounded border border-primary bg-primary/10" />
            {compatibility.materialPlan.safeZones.map((zone) => (
              <span
                className="absolute overflow-hidden rounded border border-primary bg-primary/10 px-1 py-0.5 text-[9px] font-medium text-primary"
                key={zone.id}
                style={materialBoundsStyle(zone.bounds)}
              >
                {zone.id}
              </span>
            ))}
            {compatibility.materialPlan.overlays.map((overlay) => (
              <span
                className="absolute overflow-hidden rounded border border-foreground bg-foreground px-1 py-0.5 text-[9px] font-semibold text-background"
                key={overlay.id}
                style={materialBoundsStyle(overlay.bounds)}
              >
                {overlay.label}
              </span>
            ))}
          </div>
          <p className="mt-24 text-center text-xs text-secondary-foreground">
            {status === "loading"
              ? "正在准备 3D 预览。"
              : "WebGL 不可用，显示结构化 3D 占位预览。"}
          </p>
        </div>
      ) : null}
    </div>
  );
}

function materialBoundsStyle(bounds: {
  height: number;
  width: number;
  x: number;
  y: number;
}): CSSProperties {
  return {
    height: `${bounds.height * 100}%`,
    left: `${bounds.x * 100}%`,
    top: `${bounds.y * 100}%`,
    width: `${bounds.width * 100}%`,
  };
}

function prefersReducedMotion(): boolean {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
}
