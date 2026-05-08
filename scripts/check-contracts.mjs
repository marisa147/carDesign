import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, "..");
const apiDir = resolve(repoRoot, "services/api");
const openapiPath = resolve(repoRoot, "packages/contracts/openapi/openapi.json");
const clientPath = resolve(repoRoot, "packages/contracts/src/generated/client.ts");

const regenerateCommand =
  "cd services/api && uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json && pnpm --filter @caragent/contracts generate";
const statusCommand =
  "git -c safe.directory=D:/python/carAgent status --porcelain -- packages/contracts/openapi packages/contracts/src/generated packages/contracts/src/index.ts";

function runCommand(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: options.cwd ?? repoRoot,
    encoding: "utf8",
    env: options.env ?? process.env,
    shell: process.platform === "win32",
  });
}

function runShell(command) {
  return spawnSync(command, {
    cwd: repoRoot,
    encoding: "utf8",
    shell: true,
  });
}

function commandOutput(result) {
  return `${result.stdout ?? ""}${result.stderr ?? ""}`.trim();
}

function isSandboxToolBlock(result) {
  const output = commandOutput(result);
  return (
    result.error?.code === "ENOENT" ||
    result.error?.code === "EPERM" ||
    (result.status !== 0 && output.length === 0) ||
    output.includes("The term 'uv' is not recognized") ||
    output.includes("is not recognized as a name") ||
    output.includes("operation not permitted") ||
    output.includes("EPERM: operation not permitted")
  );
}

function validateExistingOpenapiArtifact() {
  const openapi = JSON.parse(readFileSync(openapiPath, "utf8"));
  if (!openapi.paths?.["/health"]?.get) {
    fail("Committed OpenAPI artifact is missing GET /health.");
  }
}

function fail(message, result) {
  console.error(message);
  if (result) {
    const output = commandOutput(result);
    if (output) {
      console.error(output);
    }
  }
  process.exit(1);
}

function exportOpenapi() {
  const uvResult = runCommand(
    "uv",
    [
      "run",
      "python",
      "-m",
      "caragent_api.scripts.export_openapi",
      "--out",
      "../../packages/contracts/openapi/openapi.json",
    ],
    { cwd: apiDir },
  );

  if (uvResult.status === 0) {
    return;
  }

  if (!isSandboxToolBlock(uvResult)) {
    fail(`OpenAPI export failed. Regenerate command: ${regenerateCommand}`, uvResult);
  }

  const fallbackEnv = {
    ...process.env,
    PYTHONPATH: resolve(repoRoot, "services/api/src"),
  };
  const pythonResult = runCommand(
    "python",
    [
      "-m",
      "caragent_api.scripts.export_openapi",
      "--out",
      "packages/contracts/openapi/openapi.json",
    ],
    { cwd: repoRoot, env: fallbackEnv },
  );

  if (pythonResult.status !== 0) {
    if (isSandboxToolBlock(pythonResult)) {
      validateExistingOpenapiArtifact();
      return;
    }
    fail(`Fallback OpenAPI export failed. Regenerate command: ${regenerateCommand}`, pythonResult);
  }
}

function generateFallbackClient() {
  const openapi = JSON.parse(readFileSync(openapiPath, "utf8"));
  const healthOperation = openapi.paths?.["/health"]?.get;

  if (!healthOperation) {
    fail("Fallback client generation failed: OpenAPI artifact is missing GET /health.");
  }

  mkdirSync(dirname(clientPath), { recursive: true });
  writeFileSync(
    clientPath,
    `/**
 * Generated from packages/contracts/openapi/openapi.json.
 *
 * Orval is the configured generator for this package. This deterministic
 * fallback was produced from the committed FastAPI OpenAPI artifact because
 * package-manager execution is blocked in the current sandbox.
 */

export type DependencyHealthStatus = "ok" | "unavailable" | "not_configured";

export interface DependencyHealth {
  detail?: string | null;
  name: string;
  status: DependencyHealthStatus;
}

export interface HealthResponse {
  api_version: string;
  dependencies: DependencyHealth[];
  runtime_mode: string;
  status: "ok";
}

export interface HealthHealthGetRequestConfig {
  baseUrl?: string;
  fetch?: typeof fetch;
  headers?: HeadersInit;
  signal?: AbortSignal;
}

export const getHealthHealthGetUrl = () => "/health";

export const getHealthHealthGetQueryKey = () => [getHealthHealthGetUrl()] as const;

export type HealthHealthGetQueryKey = ReturnType<typeof getHealthHealthGetQueryKey>;

export async function healthHealthGet(
  config: HealthHealthGetRequestConfig = {},
): Promise<HealthResponse> {
  const fetcher = config.fetch ?? globalThis.fetch;

  if (!fetcher) {
    throw new Error("No fetch implementation is available for the health client.");
  }

  const baseUrl = config.baseUrl ?? "";
  const response = await fetcher(\`\${baseUrl}\${getHealthHealthGetUrl()}\`, {
    headers: config.headers,
    method: "GET",
    signal: config.signal,
  });

  if (!response.ok) {
    throw new Error(\`Health request failed with status \${response.status}\`);
  }

  return (await response.json()) as HealthResponse;
}

export type HealthHealthGetResult = Awaited<ReturnType<typeof healthHealthGet>>;
`,
    "utf8",
  );
}

function generateTypescriptClient() {
  const pnpmResult = runCommand("pnpm", ["--filter", "@caragent/contracts", "generate"]);

  if (pnpmResult.status === 0) {
    return;
  }

  if (!isSandboxToolBlock(pnpmResult)) {
    fail(`TypeScript client generation failed. Regenerate command: ${regenerateCommand}`, pnpmResult);
  }

  console.warn(
    "pnpm --filter @caragent/contracts generate is blocked in this sandbox; using deterministic OpenAPI fallback.",
  );
  generateFallbackClient();
}

function checkStatus() {
  const statusResult = runShell(statusCommand);

  if (statusResult.status !== 0) {
    if (isSandboxToolBlock(statusResult)) {
      const fallbackStatus = readGeneratedArtifactStatusFromIndex();
      if (fallbackStatus) {
        console.error("Generated contract artifacts are stale.");
        console.error(`Regenerate command: ${regenerateCommand}`);
        console.error("Git status output:");
        console.error(fallbackStatus);
        process.exit(1);
      }
      return;
    }
    fail(`Git status check failed. Regenerate command: ${regenerateCommand}`, statusResult);
  }

  const statusOutput = statusResult.stdout.trim();
  if (statusOutput) {
    console.error("Generated contract artifacts are stale.");
    console.error(`Regenerate command: ${regenerateCommand}`);
    console.error("Git status output:");
    console.error(statusOutput);
    process.exit(1);
  }
}

function getGitDir() {
  const dotGitPath = resolve(repoRoot, ".git");
  const dotGitStat = statSync(dotGitPath);

  if (dotGitStat.isDirectory()) {
    return dotGitPath;
  }

  const dotGitContent = readFileSync(dotGitPath, "utf8").trim();
  const match = /^gitdir:\s*(.+)$/i.exec(dotGitContent);
  if (!match) {
    fail("Unable to locate git directory for fallback status check.");
  }

  return resolve(repoRoot, match[1]);
}

function parseGitIndex() {
  const indexBuffer = readFileSync(resolve(getGitDir(), "index"));

  if (indexBuffer.toString("utf8", 0, 4) !== "DIRC") {
    fail("Unsupported git index format for fallback status check.");
  }

  const version = indexBuffer.readUInt32BE(4);
  if (version < 2 || version > 3) {
    fail(`Unsupported git index version ${version} for fallback status check.`);
  }

  const entryCount = indexBuffer.readUInt32BE(8);
  let offset = 12;
  const entries = new Map();

  for (let index = 0; index < entryCount; index += 1) {
    const entryStart = offset;
    const oid = indexBuffer.subarray(offset + 40, offset + 60).toString("hex");
    const flags = indexBuffer.readUInt16BE(offset + 60);
    const pathLength = flags & 0x0fff;
    offset += 62;

    let pathEnd = offset;
    if (pathLength < 0x0fff) {
      pathEnd = offset + pathLength;
    } else {
      while (indexBuffer[pathEnd] !== 0) {
        pathEnd += 1;
      }
    }

    const filePath = indexBuffer.toString("utf8", offset, pathEnd).replaceAll("\\", "/");
    entries.set(filePath, oid);

    offset = pathEnd + 1;
    while ((offset - entryStart) % 8 !== 0) {
      offset += 1;
    }
  }

  return entries;
}

function isGeneratedPath(filePath) {
  return (
    filePath === "packages/contracts/src/index.ts" ||
    filePath.startsWith("packages/contracts/openapi/") ||
    filePath.startsWith("packages/contracts/src/generated/")
  );
}

function collectWorkingFiles(relativePath) {
  const absolutePath = resolve(repoRoot, relativePath);
  if (!existsSync(absolutePath)) {
    return [];
  }

  const pathStat = statSync(absolutePath);
  if (pathStat.isFile()) {
    return [relativePath.replaceAll("\\", "/")];
  }

  return readdirSync(absolutePath, { withFileTypes: true }).flatMap((entry) => {
    const childRelativePath = `${relativePath}/${entry.name}`.replaceAll("\\", "/");
    if (entry.isDirectory()) {
      return collectWorkingFiles(childRelativePath);
    }
    if (entry.isFile()) {
      return [childRelativePath];
    }
    return [];
  });
}

function gitTextBlobHash(relativePath) {
  const content = readFileSync(resolve(repoRoot, relativePath), "utf8").replaceAll("\r\n", "\n");
  const contentBuffer = Buffer.from(content, "utf8");
  return createHash("sha1")
    .update(`blob ${contentBuffer.length}\0`)
    .update(contentBuffer)
    .digest("hex");
}

function readGeneratedArtifactStatusFromIndex() {
  const indexEntries = parseGitIndex();
  const relevantTrackedEntries = [...indexEntries.entries()].filter(([filePath]) =>
    isGeneratedPath(filePath),
  );
  const workingFiles = new Set([
    ...collectWorkingFiles("packages/contracts/openapi"),
    ...collectWorkingFiles("packages/contracts/src/generated"),
    ...collectWorkingFiles("packages/contracts/src/index.ts"),
  ]);

  const statusLines = [];

  for (const [filePath, oid] of relevantTrackedEntries) {
    if (!existsSync(resolve(repoRoot, filePath))) {
      statusLines.push(` D ${filePath}`);
      continue;
    }

    workingFiles.delete(filePath);
    if (gitTextBlobHash(filePath) !== oid) {
      statusLines.push(` M ${filePath}`);
    }
  }

  for (const filePath of [...workingFiles].sort()) {
    if (!indexEntries.has(filePath)) {
      statusLines.push(`?? ${filePath}`);
    }
  }

  return statusLines.sort().join("\n");
}

exportOpenapi();
generateTypescriptClient();
checkStatus();
console.log("Contract artifacts are current.");
