import assert from "node:assert/strict";

import {
  buildHostCommandInvocation,
  buildHostPrereqReport,
  isUserProfilePermissionError,
  parsePackageManagerSpec,
} from "./check-host-prereqs.mjs";

assert.deepEqual(parsePackageManagerSpec("pnpm@11.0.8"), {
  manager: "pnpm",
  version: "11.0.8",
});

assert.deepEqual(buildHostCommandInvocation("pnpm", ["--version"], "win32"), {
  command: "cmd.exe",
  args: ["/d", "/s", "/c", "pnpm --version"],
});

assert.deepEqual(buildHostCommandInvocation("uv", ["--version"], "win32"), {
  command: "uv",
  args: ["--version"],
});

assert.deepEqual(
  buildHostCommandInvocation(
    "corepack",
    ["pnpm", "--version"],
    "win32",
    "C:\\nvm4w\\nodejs\\node.exe",
  ),
  {
    command: "cmd.exe",
    args: ["/d", "/s", "/c", "C:\\nvm4w\\nodejs\\corepack.cmd pnpm --version"],
  },
);

assert.deepEqual(buildHostCommandInvocation("corepack", ["pnpm", "--version"], "linux"), {
  command: "corepack",
  args: ["pnpm", "--version"],
});

assert.deepEqual(buildHostCommandInvocation("pnpm", ["--version"], "linux"), {
  command: "pnpm",
  args: ["--version"],
});

assert.equal(
  isUserProfilePermissionError(
    "Error: EPERM: operation not permitted, lstat 'C:\\Users\\someone\\AppData\\Local\\nvm'",
  ),
  true,
);

const report = buildHostPrereqReport({
  expectedNodeVersion: "22.15.0",
  expectedPackageManager: "pnpm@11.0.8",
  expectedPythonVersion: "3.13.13",
  nodeVersion: "20.12.0",
  runCommand(command, args) {
    if (command === "pnpm") {
      return {
        status: 1,
        stdout: "",
        stderr: "EPERM: operation not permitted, lstat 'C:\\Users\\dev'",
      };
    }

    if (command === "corepack") {
      return {
        status: 1,
        stdout: "",
        stderr: "EPERM: operation not permitted, lstat 'C:\\Users\\dev'",
      };
    }

    if (command === "python") {
      return { status: 0, stdout: "Python 3.11.5\n", stderr: "" };
    }

    if (command === "uv" && args?.[0] === "run") {
      return { status: 1, stdout: "", stderr: "No interpreter found" };
    }

    if (command === "uv") {
      return {
        status: null,
        stdout: "",
        stderr: "",
        error: { code: "ENOENT", message: "not found" },
      };
    }

    throw new Error(`unexpected command ${command}`);
  },
});

assert.equal(report.ok, false);
assert.match(report.failures.join("\n"), /Node\.js 22\.15\.0 required/);
assert.match(report.failures.join("\n"), /pnpm 11\.0\.8 required/);
assert.match(report.failures.join("\n"), /Windows user profile path/);
assert.match(report.failures.join("\n"), /Python 3\.13\.13 required/);
assert.match(report.failures.join("\n"), /uv is required/);

const uvManagedReport = buildHostPrereqReport({
  expectedNodeVersion: "22.15.0",
  expectedPackageManager: "pnpm@11.0.8",
  expectedPythonVersion: "3.13.13",
  nodeVersion: "22.15.0",
  runCommand(command, args) {
    if (command === "pnpm") {
      return {
        status: 1,
        stdout: "",
        stderr: "'pnpm' is not recognized as an internal or external command",
      };
    }

    if (command === "corepack" && args?.join(" ") === "pnpm --version") {
      return { status: 0, stdout: "11.0.8\n", stderr: "" };
    }

    if (command === "uv" && args?.join(" ") === "--version") {
      return { status: 0, stdout: "uv 0.11.16\n", stderr: "" };
    }

    if (command === "uv" && args?.join(" ") === "run python --version") {
      return { status: 0, stdout: "Python 3.13.13\n", stderr: "" };
    }

    if (command === "python") {
      return { status: 0, stdout: "Python 3.11.5\n", stderr: "" };
    }

    throw new Error(`unexpected command ${command} ${args?.join(" ")}`);
  },
});

assert.equal(uvManagedReport.ok, true);

console.log("check-host-prereqs tests passed.");
