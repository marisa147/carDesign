const args = process.argv.slice(2);
const isDryRun = args.includes("--dry-run");
const apiBaseUrl =
  readArgValue("--api-base-url") ?? process.env.CARAGENT_API_BASE_URL ?? "http://127.0.0.1:8000";
const timeoutMs = Number.parseInt(readArgValue("--timeout-ms") ?? "90000", 10);
const pollIntervalMs = Number.parseInt(readArgValue("--poll-interval-ms") ?? "1000", 10);

async function main() {
  if (isDryRun) {
    runDryRun();
    return;
  }

  assertTimeouts();
  console.log(`Running worker queue smoke against ${apiBaseUrl}.`);

  const operations = await requestJson("/operations/provider-status", {
    expected: "operations status",
    method: "GET",
  });
  if (operations.worker?.status !== "ok") {
    throw new Error(
      `Worker unavailable via operations status (${operations.worker?.status ?? "unknown"}): ${
        operations.worker?.detail ?? "no detail"
      }`,
    );
  }

  const workspace = await requestJson("/workspaces", {
    body: { title: "Worker smoke workspace" },
    expected: "workspace create",
    method: "POST",
  });
  const brief = await requestJson(`/workspaces/${workspace.id}/generation/briefs`, {
    body: {
      character_focus: "door heroine with rear quarter mascot",
      character_theme: "Sakura heroine",
      color_harmony: "white base with teal accents",
      coverage: "balanced side coverage",
      original_request: "White coupe with Sakura heroine, teal accents, and MOON DRIVE text.",
      overlay_logo_asset_ids: [],
      palette: ["white", "teal"],
      racing_cues: ["number panel", "tow arrow"],
      reference_asset_ids: [],
      style: "clean racing itasha",
      supporting_graphics: ["sakura petals", "teal ribbon"],
      text: ["MOON DRIVE"],
      typography_intent: "bold readable door lettering",
      vehicle_template_id: "generic-side-coupe",
      view: "side",
    },
    expected: "generation brief create",
    method: "POST",
  });
  const submission = await requestJson(`/workspaces/${workspace.id}/generation/jobs`, {
    body: {
      brief_id: brief.id,
      idempotency_key: `worker-smoke-${Date.now()}`,
      requested_by: "smoke-worker-queue",
    },
    expected: "generation job submit",
    method: "POST",
  });

  const jobId = submission.job.id;
  const finalJob = await pollJob(jobId);
  if (finalJob.status !== "succeeded") {
    const events = await requestJson(`/jobs/${jobId}/events`, {
      expected: "job events",
      method: "GET",
    }).catch(() => []);
    const latestEvent = Array.isArray(events) ? events.at(-1) : null;
    throw new Error(
      `Worker smoke job ${jobId} ended with ${finalJob.status}: ${
        finalJob.latest_error ?? latestEvent?.message ?? "no error detail"
      }`,
    );
  }

  const [events, artifacts, versions] = await Promise.all([
    requestJson(`/jobs/${jobId}/events`, { expected: "job events", method: "GET" }),
    requestJson(`/workspaces/${workspace.id}/artifacts`, {
      expected: "workspace artifacts",
      method: "GET",
    }),
    requestJson(`/workspaces/${workspace.id}/versions`, {
      expected: "workspace versions",
      method: "GET",
    }),
  ]);
  const version = Array.isArray(versions)
    ? versions.find((candidate) => candidate.job_id === jobId)
    : null;
  const artifact = Array.isArray(artifacts)
    ? artifacts.find((candidate) => candidate.job_id === jobId)
    : null;
  const previewSpec = version?.parameters?.preview_spec;

  if (!artifact) {
    throw new Error(`Worker smoke job ${jobId} succeeded without a generated artifact.`);
  }
  if (!version) {
    throw new Error(`Worker smoke job ${jobId} succeeded without a design version.`);
  }
  if (!previewSpec?.canvas || !Array.isArray(previewSpec.safe_zones)) {
    throw new Error(`Worker smoke job ${jobId} did not persist PreviewSpec metadata.`);
  }

  console.log("Worker queue smoke passed.");
  console.log(`Workspace: ${workspace.id}`);
  console.log(`Job: ${jobId}`);
  console.log(`Version: ${version.id}`);
  console.log(`Artifact: ${artifact.id}`);
  console.log(`Events: ${Array.isArray(events) ? events.length : 0}`);
}

function runDryRun() {
  assertTimeouts();
  console.log("Worker queue smoke dry run passed.");
  console.log(`API base URL: ${apiBaseUrl}`);
  console.log("Real smoke prerequisites:");
  console.log("  pnpm infra:up");
  console.log("  cd services/api; uv run alembic upgrade head");
  console.log("  pnpm dev:api");
  console.log(
    "  cd services/worker; uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1",
  );
  console.log("  pnpm smoke:worker");
}

async function pollJob(jobId) {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    const job = await requestJson(`/jobs/${jobId}`, {
      expected: `job ${jobId}`,
      method: "GET",
    });
    if (["succeeded", "failed", "canceled"].includes(job.status)) {
      return job;
    }
    await delay(pollIntervalMs);
  }

  throw new Error(`Worker smoke timed out after ${timeoutMs}ms waiting for job ${jobId}.`);
}

async function requestJson(path, options) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    headers: options.body === undefined ? undefined : { "Content-Type": "application/json" },
    method: options.method,
  }).catch((error) => {
    throw new Error(`Failed to reach API for ${options.expected}: ${error.message}`);
  });

  const text = await response.text();
  const body = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(
      `API ${options.expected} failed with HTTP ${response.status}: ${JSON.stringify(body)}`,
    );
  }

  return body;
}

function readArgValue(name) {
  const prefix = `${name}=`;
  return args.find((arg) => arg.startsWith(prefix))?.slice(prefix.length) ?? null;
}

function assertTimeouts() {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error("--timeout-ms must be a positive integer.");
  }
  if (!Number.isFinite(pollIntervalMs) || pollIntervalMs <= 0) {
    throw new Error("--poll-interval-ms must be a positive integer.");
  }
}

function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
