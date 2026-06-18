import { describe, expect, it } from "vitest";

import { publicEnv } from "./public-env";

describe("publicEnv", () => {
  it("defaults V2 capability flags off without exposing server secrets", () => {
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
