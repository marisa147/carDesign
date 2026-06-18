import { afterEach, describe, expect, it, vi } from "vitest";

const v2PublicEnvKeys = [
  "NEXT_PUBLIC_V2_HOSTED_PROVIDER_ROLLOUT_ENABLED",
  "NEXT_PUBLIC_V2_TARGETED_REGENERATION_ENABLED",
  "NEXT_PUBLIC_V2_REFERENCE_GUIDANCE_ENABLED",
  "NEXT_PUBLIC_V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED",
  "NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED",
] as const;

const loadPublicEnv = async () => {
  vi.resetModules();
  const publicEnvModule = await import("./public-env");
  return publicEnvModule.publicEnv;
};

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe("publicEnv", () => {
  it("defaults V2 capability flags off without exposing server secrets", async () => {
    for (const key of v2PublicEnvKeys) {
      vi.stubEnv(key, undefined);
    }

    const publicEnv = await loadPublicEnv();

    expect(publicEnv.v2HostedProviderRolloutEnabled).toBe(false);
    expect(publicEnv.v2TargetedRegenerationEnabled).toBe(false);
    expect(publicEnv.v2ReferenceGuidanceEnabled).toBe(false);
    expect(publicEnv.v2Lightweight3dPreviewEnabled).toBe(false);
    expect(publicEnv.v2EnhancedHandoffPackageEnabled).toBe(false);

    const rendered = JSON.stringify(publicEnv).toLowerCase();

    expect(rendered).not.toContain("api_key");
    expect(rendered).not.toContain("secret");
    expect(rendered).not.toContain("database_url");
    expect(rendered).not.toContain("redis_url");
    expect(rendered).not.toContain("s3_");
  });
});
