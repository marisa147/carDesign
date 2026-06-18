import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  buildHostPrereqReport,
  formatHostPrereqFailures,
  isUserProfilePermissionError,
  readExpectedPrereqs,
  runHostCommand,
} from "./check-host-prereqs.mjs";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const requiredCommands = [
  {
    display: "node scripts/check-host-prereqs.mjs",
    inlineFunction: () => {
      const report = buildHostPrereqReport(readExpectedPrereqs());
      if (!report.ok) {
        throw new Error(formatHostPrereqFailures(report));
      }
      console.log("Host prerequisites are available for Phase 3 validation.");
    },
  },
  {
    display: "node scripts/check-env-examples.mjs",
    inlineModule: "./check-env-examples.mjs",
  },
  {
    display: "pnpm --filter @caragent/web lint",
    command: "pnpm",
    args: ["--filter", "@caragent/web", "lint"],
  },
  {
    display: "pnpm --filter @caragent/web typecheck",
    command: "pnpm",
    args: ["--filter", "@caragent/web", "typecheck"],
  },
  {
    display: "pnpm --filter @caragent/web test",
    command: "pnpm",
    args: ["--filter", "@caragent/web", "test"],
  },
  {
    display: "cd services/core && uv run ruff check .",
    command: "uv",
    args: ["run", "ruff", "check", "."],
    cwd: "services/core",
  },
  {
    display: "cd services/core && uv run mypy src",
    command: "uv",
    args: ["run", "mypy", "src"],
    cwd: "services/core",
  },
  {
    display: "cd services/core && uv run pytest -q",
    command: "uv",
    args: ["run", "pytest", "-q"],
    cwd: "services/core",
  },
  {
    display: "cd services/api && uv run ruff check .",
    command: "uv",
    args: ["run", "ruff", "check", "."],
    cwd: "services/api",
  },
  {
    display: "cd services/api && uv run mypy src",
    command: "uv",
    args: ["run", "mypy", "src"],
    cwd: "services/api",
  },
  {
    display: "cd services/api && uv run pytest -q",
    command: "uv",
    args: ["run", "pytest", "-q"],
    cwd: "services/api",
  },
  {
    display: "cd services/worker && uv run ruff check .",
    command: "uv",
    args: ["run", "ruff", "check", "."],
    cwd: "services/worker",
  },
  {
    display: "cd services/worker && uv run mypy src",
    command: "uv",
    args: ["run", "mypy", "src"],
    cwd: "services/worker",
  },
  {
    display: "cd services/worker && uv run pytest -q",
    command: "uv",
    args: ["run", "pytest", "-q"],
    cwd: "services/worker",
  },
  {
    display: "pnpm contracts:check",
    command: "pnpm",
    args: ["contracts:check"],
  },
  {
    display: "pnpm --filter @caragent/contracts typecheck",
    command: "pnpm",
    args: ["--filter", "@caragent/contracts", "typecheck"],
  },
];

console.log("Phase 3 aggregate validation");
console.log(
  "Docker-dependent Phase 2/3 smoke is not part of this required sequence. Run pnpm smoke:local after pnpm infra:up when Docker is available.",
);

for (const command of requiredCommands) {
  await runRequiredCommand(command);
}

console.log("\nPhase 3 aggregate validation passed.");

async function runRequiredCommand(command) {
  console.log(`\n$ ${command.display}`);

  if (command.inlineModule || command.inlineFunction) {
    try {
      if (command.inlineFunction) {
        command.inlineFunction();
      } else {
        await import(new URL(command.inlineModule, import.meta.url));
      }
    } catch (error) {
      console.error(`\nValidation command failed: ${command.display}`);
      console.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
    return;
  }

  const result = runValidationCommand(command);

  writeOutput(result);

  if (result.error) {
    console.error(`\nValidation command failed: ${command.display}`);
    console.error(result.error.message);
    printHostPrerequisiteHint(command, result);
    process.exit(1);
  }

  if (result.status !== 0) {
    console.error(`\nValidation command failed: ${command.display}`);
    printHostPrerequisiteHint(command, result);
    process.exit(result.status ?? 1);
  }
}

function runValidationCommand(command) {
  const options = {
    cwd: command.cwd ? resolve(repoRoot, command.cwd) : repoRoot,
  };
  if (command.command === "pnpm") {
    return runHostCommand("corepack", ["pnpm", ...command.args], options);
  }

  return runHostCommand(command.command, command.args, options);
}

function writeOutput(result) {
  if (result.stdout) {
    process.stdout.write(result.stdout);
  }

  if (result.stderr) {
    process.stderr.write(result.stderr);
  }
}

function printHostPrerequisiteHint(command, result) {
  const output = `${result.stdout ?? ""}\n${result.stderr ?? ""}\n${result.error?.message ?? ""}`;

  if (
    isUserProfilePermissionError(output) ||
    (command.display.startsWith("pnpm ") && result.error?.code === "EPERM")
  ) {
    console.error(
      "Host prerequisite blocked: Node/pnpm cannot access the Windows user profile path in this shell. Re-run pnpm validate on an unrestricted host shell or configure a writable Corepack home.",
    );
    return;
  }

  if (command.display.startsWith("pnpm ") && result.error?.code === "ENOENT") {
    console.error(
      "Host prerequisite blocked: pnpm is not available to this Node process. Install/enable pnpm 11.x, then re-run pnpm validate.",
    );
    return;
  }

  if (
    command.display.includes("uv run") &&
    (output.includes("uv") || output.includes("is not recognized") || result.error?.code === "ENOENT")
  ) {
    console.error(
      "Host prerequisite blocked: uv is not installed or not available on PATH. Install uv, run the service uv sync commands, then re-run pnpm validate.",
    );
  }
}
