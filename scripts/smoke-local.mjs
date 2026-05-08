import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import http from "node:http";
import net from "node:net";

const args = new Set(process.argv.slice(2));
const shouldManageCompose = args.has("--with-compose-if-docker");
const dockerInfoCommand = "docker info";
const composeUpCommand = "pnpm infra:up";
const composeDownCommand = "pnpm infra:down";

const env = parseEnvFile(".env.example");
const serviceChecks = [
  {
    name: "PostgreSQL",
    run: () => checkTcp("127.0.0.1", numberFromEnv("POSTGRES_PORT", 5432)),
  },
  {
    name: "Redis",
    run: () => checkRedis("127.0.0.1", numberFromEnv("REDIS_PORT", 6379)),
  },
  {
    name: "MinIO",
    run: () => checkMinio(),
  },
];

async function main() {
  const docker = runCommand(dockerInfoCommand, { stdio: "pipe" });
  if (!docker.ok) {
    console.log(
      "Docker daemon unavailable; enable Docker Desktop or Docker Engine, then run pnpm infra:up, pnpm smoke:local, and pnpm infra:down.",
    );
    process.exit(0);
  }

  if (shouldManageCompose) {
    const up = runCommand(composeUpCommand);
    if (!up.ok) {
      process.exit(up.status ?? 1);
    }
  }

  try {
    await runServiceChecks(shouldManageCompose ? 30 : 3);
  } catch (error) {
    console.error(error.message);
    if (!shouldManageCompose) {
      console.error(
        "Start services with pnpm infra:up first, or run node scripts/smoke-local.mjs --with-compose-if-docker.",
      );
    }
    process.exitCode = 1;
  } finally {
    if (shouldManageCompose) {
      const down = runCommand(composeDownCommand);
      if (!down.ok && process.exitCode === undefined) {
        process.exitCode = down.status ?? 1;
      }
    }
  }
}

function parseEnvFile(filePath) {
  const values = new Map();
  const content = readFileSync(filePath, "utf8");

  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    const separator = trimmed.indexOf("=");
    if (separator === -1) {
      continue;
    }

    values.set(trimmed.slice(0, separator), trimmed.slice(separator + 1));
  }

  return values;
}

function numberFromEnv(key, fallback) {
  const value = Number.parseInt(process.env[key] ?? env.get(key) ?? String(fallback), 10);
  if (!Number.isFinite(value)) {
    throw new Error(`${key} must be a numeric port`);
  }

  return value;
}

function runCommand(command, options = {}) {
  const result = spawnSync(command, {
    shell: true,
    stdio: options.stdio ?? "inherit",
    windowsHide: true,
  });

  if (result.error) {
    return { ok: false, status: 1, error: result.error };
  }

  return { ok: result.status === 0, status: result.status };
}

async function runServiceChecks(maxAttempts) {
  for (const service of serviceChecks) {
    await retry(service.name, service.run, maxAttempts);
  }

  console.log("Local PostgreSQL, Redis, and MinIO smoke checks passed.");
}

async function retry(name, check, maxAttempts) {
  let lastError;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      await check();
      console.log(`${name} check passed.`);
      return;
    } catch (error) {
      lastError = error;
      if (attempt < maxAttempts) {
        await delay(1000);
      }
    }
  }

  throw new Error(`${name} check failed: ${lastError?.message ?? "unknown error"}`);
}

function checkTcp(host, port) {
  return new Promise((resolve, reject) => {
    const socket = net.createConnection({ host, port });
    const timer = setTimeout(() => {
      socket.destroy();
      reject(new Error(`timed out connecting to ${host}:${port}`));
    }, 2000);

    socket.once("connect", () => {
      clearTimeout(timer);
      socket.end();
      resolve();
    });
    socket.once("error", (error) => {
      clearTimeout(timer);
      reject(error);
    });
  });
}

function checkRedis(host, port) {
  return new Promise((resolve, reject) => {
    const socket = net.createConnection({ host, port });
    const timer = setTimeout(() => {
      socket.destroy();
      reject(new Error(`timed out connecting to ${host}:${port}`));
    }, 2000);

    socket.once("connect", () => {
      socket.write("*1\r\n$4\r\nPING\r\n");
    });
    socket.on("data", (data) => {
      clearTimeout(timer);
      const response = data.toString("utf8");
      socket.end();
      if (response.startsWith("+PONG")) {
        resolve();
      } else {
        reject(new Error(`unexpected Redis response: ${response.trim()}`));
      }
    });
    socket.once("error", (error) => {
      clearTimeout(timer);
      reject(error);
    });
  });
}

function checkMinio() {
  const endpoint = new URL(env.get("S3_ENDPOINT_URL") ?? "http://localhost:9000");
  const requestOptions = {
    hostname: endpoint.hostname,
    port: endpoint.port || 80,
    path: "/minio/health/live",
    method: "GET",
    timeout: 2000,
  };

  return new Promise((resolve, reject) => {
    const request = http.request(requestOptions, (response) => {
      response.resume();
      if (response.statusCode && response.statusCode >= 200 && response.statusCode < 300) {
        resolve();
      } else {
        reject(new Error(`HTTP ${response.statusCode}`));
      }
    });

    request.once("timeout", () => {
      request.destroy(new Error("timed out calling /minio/health/live"));
    });
    request.once("error", reject);
    request.end();
  });
}

function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

main();
