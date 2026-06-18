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

  checkPackageManagerCommand({
    failures,
    packageManager,
    runCommand,
  });

  const uv = runCommand("uv", ["--version"]);
  if (uv.error || uv.status !== 0) {
    failures.push(
      `uv is required on PATH for Python service checks; install/enable uv and run uv sync --dev in services/api and services/worker.`,
    );
    checkVersionedCommand({
      command: "python",
      args: ["--version"],
      expectedVersion: expectedPythonVersion,
      failures,
      label: "Python",
      parseVersion: parseSemver,
      runCommand,
    });
  } else {
    checkVersionedCommand({
      command: "uv",
      args: ["run", "python", "--version"],
      expectedVersion: expectedPythonVersion,
      failures,
      label: "Python",
      parseVersion: parseSemver,
      runCommand,
    });
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

function checkPackageManagerCommand({ failures, packageManager, runCommand }) {
  const direct = runCommand(packageManager.manager, ["--version"]);
  if (commandMatchesVersion(direct, packageManager.version)) {
    return;
  }

  const corepack = runCommand("corepack", [packageManager.manager, "--version"]);
  if (commandMatchesVersion(corepack, packageManager.version)) {
    return;
  }

  const attempts = [direct, corepack];
  const profileBlocked = attempts.some((result) => {
    const output = commandOutput(result);
    return result.error?.code === "EPERM" || isUserProfilePermissionError(output);
  });

  if (profileBlocked) {
    failures.push(
      `${packageManager.manager} ${packageManager.version} required; ${packageManager.manager} cannot start cleanly in this shell, commonly because Node/Corepack resolves through a Windows user profile path that is blocked. Fix: open an unrestricted host shell, or set NODE_OPTIONS="--preserve-symlinks --preserve-symlinks-main" and COREPACK_HOME to a writable directory before running corepack prepare ${packageManager.manager}@${packageManager.version} --activate.`,
    );
    return;
  }

  const foundVersion = attempts.map(commandOutput).map(parseSemver).find(Boolean);
  if (foundVersion) {
    failures.push(`${packageManager.manager} ${packageManager.version} required; found ${foundVersion}.`);
    return;
  }

  const directOutput = commandOutput(direct);
  const corepackOutput = commandOutput(corepack);
  const detail = [directOutput, corepackOutput].filter(Boolean).join(" | ");
  failures.push(
    `${packageManager.manager} ${packageManager.version} required; neither direct ${packageManager.manager} nor corepack ${packageManager.manager} could report the expected version.${detail ? ` Output: ${singleLine(detail)}` : ""}`,
  );
}

function commandMatchesVersion(result, expectedVersion) {
  return !result.error && result.status === 0 && parseSemver(commandOutput(result)) === expectedVersion;
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

export function buildHostCommandInvocation(
  command,
  args,
  platform = process.platform,
  nodeExecPath = process.execPath,
) {
  if (platform === "win32" && command === "pnpm") {
    return {
      command: "cmd.exe",
      args: ["/d", "/s", "/c", [command, ...args].map(quoteWindowsCmdArg).join(" ")],
    };
  }

  if (platform === "win32" && command === "corepack") {
    const corepackCommand = resolve(dirname(nodeExecPath), "corepack.cmd");
    return {
      command: "cmd.exe",
      args: [
        "/d",
        "/s",
        "/c",
        [corepackCommand, ...args].map(quoteWindowsCmdArg).join(" "),
      ],
    };
  }

  return { command, args };
}

export function runHostCommand(command, args, options = {}) {
  const invocation = buildHostCommandInvocation(
    command,
    args,
    options.platform ?? process.platform,
    options.nodeExecPath ?? process.execPath,
  );

  return spawnSync(invocation.command, invocation.args, {
    cwd: options.cwd ?? repoRoot,
    encoding: "utf8",
    shell: false,
    windowsHide: true,
  });
}

function quoteWindowsCmdArg(value) {
  if (value === "") {
    return '""';
  }

  if (!/[ \t"]/u.test(value)) {
    return value;
  }

  return `"${value.replace(/"/gu, '\\"')}"`;
}

function main() {
  const report = buildHostPrereqReport(readExpectedPrereqs());

  if (report.ok) {
    console.log("Host prerequisites are available for Phase 2 validation.");
    return;
  }

  console.error(formatHostPrereqFailures(report));
  process.exit(1);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
