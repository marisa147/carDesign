import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(fileURLToPath(new URL("..", import.meta.url)));

const envFiles = [
  ".env.example",
  "apps/web/.env.example",
  "services/api/.env.example",
  "services/worker/.env.example",
];

const requiredByFile = {
  ".env.example": [
    "RUNTIME_MODE",
    "WEB_PORT",
    "API_PORT",
    "POSTGRES_PORT",
    "REDIS_PORT",
    "MINIO_API_PORT",
    "MINIO_CONSOLE_PORT",
    "DATABASE_URL",
    "REDIS_URL",
    "S3_ENDPOINT_URL",
    "S3_ACCESS_KEY_ID",
    "S3_SECRET_ACCESS_KEY",
    "S3_BUCKET",
    "CORS_ORIGINS",
    "NEXT_PUBLIC_API_BASE_URL",
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_PROVIDER_OPENAI_API_KEY",
    "AI_PROVIDER_FAL_API_KEY",
    "AI_PROVIDER_BFL_API_KEY",
  ],
  "apps/web/.env.example": [
    "RUNTIME_MODE",
    "WEB_PORT",
    "NEXT_PUBLIC_API_BASE_URL",
    "NEXT_PUBLIC_RUNTIME_MODE",
  ],
  "services/api/.env.example": [
    "RUNTIME_MODE",
    "API_PORT",
    "DATABASE_URL",
    "REDIS_URL",
    "S3_ENDPOINT_URL",
    "S3_ACCESS_KEY_ID",
    "S3_SECRET_ACCESS_KEY",
    "S3_BUCKET",
    "CORS_ORIGINS",
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_PROVIDER_OPENAI_API_KEY",
    "AI_PROVIDER_FAL_API_KEY",
    "AI_PROVIDER_BFL_API_KEY",
  ],
  "services/worker/.env.example": [
    "RUNTIME_MODE",
    "DATABASE_URL",
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "S3_ENDPOINT_URL",
    "S3_ACCESS_KEY_ID",
    "S3_SECRET_ACCESS_KEY",
    "S3_BUCKET",
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_PROVIDER_OPENAI_API_KEY",
    "AI_PROVIDER_FAL_API_KEY",
    "AI_PROVIDER_BFL_API_KEY",
  ],
};

const realEnvTrackedPatterns = [
  /^\.env$/,
  /^\.env\.local$/,
  /^\.env\..*\.local$/,
  /^apps\/web\/\.env$/,
  /^apps\/web\/\.env\.local$/,
  /^apps\/web\/\.env\..*\.local$/,
  /^services\/api\/\.env$/,
  /^services\/api\/\.env\.local$/,
  /^services\/api\/\.env\..*\.local$/,
  /^services\/worker\/\.env$/,
  /^services\/worker\/\.env\.local$/,
  /^services\/worker\/\.env\..*\.local$/,
];

const providerKeys = [
  "AI_PROVIDER_OPENAI_API_KEY",
  "AI_PROVIDER_FAL_API_KEY",
  "AI_PROVIDER_BFL_API_KEY",
];

const legacyProviderKeys = [
  "OPENAI_API_KEY",
  "STABILITY_API_KEY",
  "FAL_API_KEY",
  "REPLICATE_API_TOKEN",
];

const suspiciousSecretPatterns = [
  /sk-[A-Za-z0-9_-]{20,}/,
  /[A-Za-z0-9_=-]{32,}/,
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
];

function parseEnv(filePath) {
  const parsed = new Map();
  const lines = readFileSync(filePath, "utf8").split(/\r?\n/);

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    const separator = trimmed.indexOf("=");
    if (separator === -1) {
      throw new Error(`${filePath} has an invalid env line: ${line}`);
    }

    const key = trimmed.slice(0, separator).trim();
    const value = trimmed.slice(separator + 1).trim();
    parsed.set(key, value);
  }

  return parsed;
}

function assertRequiredKeys(file, values) {
  for (const key of requiredByFile[file]) {
    if (!values.has(key)) {
      throw new Error(`${file} missing ${key}`);
    }
  }
}

function assertLocalSecrets(file, values) {
  for (const [key, value] of values) {
    if (!/(KEY|TOKEN|SECRET|PASSWORD)$/i.test(key)) {
      continue;
    }

    if (providerKeys.includes(key) && value === "") {
      continue;
    }

    const normalized = value.toLowerCase();
    if (
      !normalized.includes("local") &&
      !normalized.includes("example") &&
      !normalized.includes("disabled") &&
      !normalized.includes("not-used")
    ) {
      throw new Error(`${file} ${key} must use an obvious local/example value`);
    }

    for (const pattern of suspiciousSecretPatterns) {
      if (pattern.test(value)) {
        throw new Error(`${file} ${key} looks like a real secret`);
      }
    }
  }
}

function assertProviderKeysOptionalInLocal(file, values) {
  if (values.get("RUNTIME_MODE") !== "local") {
    return;
  }

  if (values.has("AI_PROVIDER_CALLS_ENABLED") && values.get("AI_PROVIDER_CALLS_ENABLED") !== "false") {
    throw new Error(`${file} must keep AI_PROVIDER_CALLS_ENABLED=false in local mode`);
  }

  for (const key of providerKeys) {
    if (values.has(key) && values.get(key) !== "") {
      throw new Error(`${file} ${key} must be blank in local mode`);
    }
  }
}

function assertNoLegacyProviderKeys(file, values) {
  for (const key of legacyProviderKeys) {
    if (values.has(key)) {
      throw new Error(`${file} still uses legacy provider key ${key}`);
    }
  }
}

function assertNoTrackedRealEnvFiles() {
  let trackedFiles = [];
  try {
    const output = execFileSync(
      "git",
      ["-c", "safe.directory=D:/python/carAgent", "ls-files"],
      { cwd: repoRoot, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] },
    );
    trackedFiles = output.split(/\r?\n/).filter(Boolean);
  } catch (error) {
    trackedFiles = readTrackedFilesFromIndex();
  }

  const trackedRealEnv = trackedFiles.filter((file) =>
    realEnvTrackedPatterns.some((pattern) => pattern.test(file)),
  );

  if (trackedRealEnv.length > 0) {
    throw new Error(`Real env files are tracked: ${trackedRealEnv.join(", ")}`);
  }
}

function readTrackedFilesFromIndex() {
  const indexPath = path.join(repoRoot, ".git", "index");
  if (!existsSync(indexPath)) {
    throw new Error("Unable to inspect tracked files: .git/index is missing");
  }

  const index = readFileSync(indexPath);
  if (index.subarray(0, 4).toString("ascii") !== "DIRC") {
    throw new Error("Unable to inspect tracked files: unsupported git index");
  }

  const entryCount = index.readUInt32BE(8);
  const paths = [];
  let offset = 12;

  for (let entry = 0; entry < entryCount; entry += 1) {
    const entryStart = offset;
    const flagsOffset = offset + 60;
    const pathOffset = offset + 62;
    if (pathOffset >= index.length) {
      throw new Error("Unable to inspect tracked files: truncated git index");
    }

    const flags = index.readUInt16BE(flagsOffset);
    const pathLength = flags & 0x0fff;
    let pathEnd = pathOffset;

    if (pathLength < 0x0fff) {
      pathEnd = pathOffset + pathLength;
    } else {
      while (pathEnd < index.length && index[pathEnd] !== 0) {
        pathEnd += 1;
      }
    }

    paths.push(index.subarray(pathOffset, pathEnd).toString("utf8"));

    offset = entryStart + Math.ceil((pathEnd + 1 - entryStart) / 8) * 8;
  }

  return paths;
}

for (const file of envFiles) {
  if (!existsSync(file)) {
    throw new Error(`${file} does not exist`);
  }

  const values = parseEnv(file);
  assertRequiredKeys(file, values);
  assertLocalSecrets(file, values);
  assertProviderKeysOptionalInLocal(file, values);
  assertNoLegacyProviderKeys(file, values);
}

assertNoTrackedRealEnvFiles();
console.log("Environment examples are present, local-only, and secret-safe.");
