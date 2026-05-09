import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export function parsePackageManagerSpec(spec) {
  const separator = spec.lastIndexOf("@");
  if (separator <= 0 || separator === spec.length - 1) {
    throw new Error(`Invalid packageManager spec: ${spec}`);
  }

  return {
    manager: spec.slice(0, separator),
    version: spec.slice(separator + 1),
  };
}

export function isUserProfilePermissionError(output) {
  return (
    output.includes("EPERM") &&
    output.includes("operation not permitted") &&
    /(?:[A-Za-z]:\\Users\\[^'"`\r\n]+|\/Users\/[^'"`\r\n]+|\/home\/[^'"`\r\n]+)/.test(output)
  );
}

export function buildHostPrereqReport({
  expectedNodeVersion,
  expectedPackageManager,
  expectedPythonVersion,
  nodeVersion = process.versions.node,
  runCommand = runHostCommand,
}) {
  const failures = [];
  const packageManager = parsePackageManagerSpec(expectedPackageManager);

  if (nodeVersion !== expectedNodeVersion) {
    failures.push(
      `Node.js ${expectedNodeVersion} required; found ${nodeVersion}. Select the repo runtime from .node-version before running validation.`,
    );
  }

  checkVersionedCommand({
    command: packageManager.manager,
    args: ["--version"],
    expectedVersion: packageManager.version,
    failures,
    label: packageManager.manager,
    parseVersion: parseSemver,
    runCommand,
    userProfileFix:
      `open an unrestricted host shell, or set NODE_OPTIONS="--preserve-symlinks --preserve-symlinks-main" and COREPACK_HOME to a writable directory before running corepack prepare ${packageManager.manager}@${packageManager.version} --activate`,
  });

  checkVersionedCommand({
    command: "python",
    args: ["--version"],
    expectedVersion: expectedPythonVersion,
    failures,
    label: "Python",
    parseVersion: parseSemver,
    runCommand,
  });

  const uv = runCommand("uv", ["--version"]);
  if (uv.error || uv.status !== 0) {
    failures.push(
      `uv is required on PATH for Python service checks; install/enable uv and run uv sync --dev in services/api and services/worker.`,
    );
  }

  return {
    failures,
    ok: failures.length === 0,
  };
}

export function readExpectedPrereqs() {
  const rootPackage = JSON.parse(readFileSync(resolve(repoRoot, "package.json"), "utf8"));

  return {
    expectedNodeVersion: readFileSync(resolve(repoRoot, ".node-version"), "utf8").trim(),
    expectedPackageManager: rootPackage.packageManager,
    expectedPythonVersion: readFileSync(resolve(repoRoot, ".python-version"), "utf8").trim(),
  };
}

export function formatHostPrereqFailures(report) {
  return ["Host prerequisite check failed:", ...report.failures.map((failure) => `- ${failure}`)].join(
    "\n",
  );
}

function checkVersionedCommand({
  command,
  args,
  expectedVersion,
  failures,
  label,
  parseVersion,
  runCommand,
  userProfileFix,
}) {
  const result = runCommand(command, args);
  const output = commandOutput(result);

  if (result.error?.code === "ENOENT") {
    failures.push(`${label} ${expectedVersion} required; ${command} was not found on PATH.`);
    return;
  }

  if (result.error || result.status !== 0) {
    if ((result.error?.code === "EPERM" || isUserProfilePermissionError(output)) && userProfileFix) {
      failures.push(
        `${label} ${expectedVersion} required; ${command} cannot start cleanly in this shell, commonly because Node/Corepack resolves through a Windows user profile path that is blocked. Fix: ${userProfileFix}.`,
      );
      return;
    }

    const detail = output ? ` Output: ${singleLine(output)}` : "";
    failures.push(`${label} ${expectedVersion} required; ${command} ${args.join(" ")} failed.${detail}`);
    return;
  }

  const foundVersion = parseVersion(output);
  if (foundVersion !== expectedVersion) {
    failures.push(`${label} ${expectedVersion} required; found ${foundVersion || "unknown"}.`);
  }
}

function parseSemver(output) {
  return /v?(\d+\.\d+\.\d+)/.exec(output)?.[1] ?? "";
}

function commandOutput(result) {
  return `${result.stdout ?? ""}\n${result.stderr ?? ""}\n${result.error?.message ?? ""}`.trim();
}

function singleLine(value) {
  return value.replace(/\s+/g, " ").trim();
}

function runHostCommand(command, args) {
  return spawnSync(command, args, {
    cwd: repoRoot,
    encoding: "utf8",
    shell: false,
    windowsHide: true,
  });
}

function main() {
  const report = buildHostPrereqReport(readExpectedPrereqs());

  if (report.ok) {
    console.log("Host prerequisites are available for Phase 1 validation.");
    return;
  }

  console.error(formatHostPrereqFailures(report));
  process.exit(1);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
