import assert from "node:assert/strict";

import {
  buildHostPrereqReport,
  isUserProfilePermissionError,
  parsePackageManagerSpec,
} from "./check-host-prereqs.mjs";

assert.deepEqual(parsePackageManagerSpec("pnpm@11.0.8"), {
  manager: "pnpm",
  version: "11.0.8",
});

assert.equal(
  isUserProfilePermissionError(
    "Error: EPERM: operation not permitted, lstat 'C:\\Users\\someone\\AppData\\Local\\nvm'",
  ),
  true,
);

const report = buildHostPrereqReport({
  expectedNodeVersion: "24.15.0",
  expectedPackageManager: "pnpm@11.0.8",
  expectedPythonVersion: "3.13.13",
  nodeVersion: "20.12.0",
  runCommand(command) {
    if (command === "pnpm") {
      return {
        status: 1,
        stdout: "",
        stderr: "EPERM: operation not permitted, lstat 'C:\\Users\\dev'",
      };
    }

    if (command === "python") {
      return { status: 0, stdout: "Python 3.11.5\n", stderr: "" };
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
assert.match(report.failures.join("\n"), /Node\.js 24\.15\.0 required/);
assert.match(report.failures.join("\n"), /pnpm 11\.0\.8 required/);
assert.match(report.failures.join("\n"), /Windows user profile path/);
assert.match(report.failures.join("\n"), /Python 3\.13\.13 required/);
assert.match(report.failures.join("\n"), /uv is required/);

console.log("check-host-prereqs tests passed.");
