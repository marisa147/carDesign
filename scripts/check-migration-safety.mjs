import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const versionsDir = resolve(repoRoot, "services/api/alembic/versions");
const modelsPath = resolve(repoRoot, "services/core/src/caragent_core/models.py");

const expectedHeadRevision = "f2d60f906fc6";
const expectedLedgerTables = [
  "workspaces",
  "messages",
  "design_briefs",
  "assets",
  "generation_jobs",
  "job_events",
  "design_versions",
  "artifacts",
  "feedback",
  "exports",
  "model_runs",
];

const failures = [];

if (!existsSync(versionsDir)) {
  failNow(`Missing Alembic versions directory: ${relative(versionsDir)}`);
}

if (!existsSync(modelsPath)) {
  failNow(`Missing core models file: ${relative(modelsPath)}`);
}

const migrationFiles = readdirSync(versionsDir)
  .filter((fileName) => fileName.endsWith(".py"))
  .sort();

if (migrationFiles.length === 0) {
  failures.push("No Alembic migration files found.");
}

const migrations = migrationFiles.map((fileName) => {
  const filePath = resolve(versionsDir, fileName);
  const source = readFileSync(filePath, "utf8");
  return {
    fileName,
    revision: readPythonString(source, "revision"),
    downRevision: readPythonString(source, "down_revision"),
    source,
  };
});

const revisions = new Set(migrations.map((migration) => migration.revision).filter(Boolean));
const referencedDownRevisions = new Set(
  migrations.map((migration) => migration.downRevision).filter(Boolean),
);
const heads = migrations
  .filter((migration) => migration.revision && !referencedDownRevisions.has(migration.revision))
  .map((migration) => migration.revision)
  .sort();

if (!revisions.has(expectedHeadRevision)) {
  failures.push(`Expected Alembic revision ${expectedHeadRevision} was not found.`);
}

if (heads.length !== 1 || heads[0] !== expectedHeadRevision) {
  failures.push(
    `Expected single Alembic head ${expectedHeadRevision}; found ${heads.length ? heads.join(", ") : "none"}.`,
  );
}

for (const migration of migrations) {
  if (!migration.revision) {
    failures.push(`Migration ${migration.fileName} is missing a revision value.`);
  }
  if (migration.downRevision && !revisions.has(migration.downRevision)) {
    failures.push(
      `Migration ${migration.fileName} references missing down_revision ${migration.downRevision}.`,
    );
  }
}

const migrationSource = migrations.map((migration) => migration.source).join("\n");
const modelsSource = readFileSync(modelsPath, "utf8");

for (const tableName of expectedLedgerTables) {
  if (!migrationSource.includes(`"${tableName}"`)) {
    failures.push(`Alembic migration is missing v1 ledger table ${tableName}.`);
  }
  if (!modelsSource.includes(`__tablename__ = "${tableName}"`)) {
    failures.push(`Core models are missing v1 ledger table ${tableName}.`);
  }
}

if (failures.length > 0) {
  console.error("Migration safety check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  console.error(
    "\nStatic checks do not replace live verification. On a prepared host, also run `cd services/api && uv run alembic upgrade head && uv run alembic current`.",
  );
  process.exit(1);
}

console.log("Migration safety check passed.");
console.log(`Alembic migrations: ${migrations.length}`);
console.log(`Alembic head: ${expectedHeadRevision}`);
for (const migration of migrations) {
  console.log(
    `- ${migration.revision ?? "unknown"} (${migration.fileName}) <- ${migration.downRevision ?? "root"}`,
  );
}
console.log(`V1 ledger tables verified: ${expectedLedgerTables.join(", ")}`);

function readPythonString(source, name) {
  const stringMatch = new RegExp(`${name}:.*?=\\s*["']([^"']+)["']`).exec(source);
  if (stringMatch) {
    return stringMatch[1];
  }

  const noneMatch = new RegExp(`${name}:.*?=\\s*None`).exec(source);
  if (noneMatch) {
    return null;
  }

  return undefined;
}

function relative(filePath) {
  return filePath.replace(`${repoRoot}\\`, "").replaceAll("\\", "/");
}

function failNow(message) {
  console.error(`Migration safety check failed: ${message}`);
  process.exit(1);
}
