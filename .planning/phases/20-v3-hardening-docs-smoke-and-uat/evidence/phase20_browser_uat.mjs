import { spawn } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";

class CdpClient {
  constructor(socket) {
    this.nextId = 1;
    this.pending = new Map();
    this.socket = socket;
    socket.addEventListener("message", (event) => {
      const payload = JSON.parse(event.data);
      if (payload.id && this.pending.has(payload.id)) {
        const { reject, resolve } = this.pending.get(payload.id);
        this.pending.delete(payload.id);
        if (payload.error) {
          reject(new Error(payload.error.message));
        } else {
          resolve(payload.result ?? {});
        }
      }
    });
  }

  static async connect(url) {
    const socket = new WebSocket(url);
    await new Promise((resolve, reject) => {
      socket.addEventListener("open", resolve, { once: true });
      socket.addEventListener("error", reject, { once: true });
    });
    return new CdpClient(socket);
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.socket.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { reject, resolve });
    });
  }

  async close() {
    this.socket.close();
  }
}

const args = new Map(
  process.argv.slice(2).map((arg) => {
    const [key, ...rest] = arg.split("=");
    return [key, rest.join("=") || "true"];
  }),
);

const chromePath = args.get("--chrome") ?? "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const url = args.get("--url") ?? "http://127.0.0.1:3140";
const seedPath = args.get("--seed");
const outDir = resolve(args.get("--out-dir") ?? ".");
const port = Number.parseInt(args.get("--port") ?? "9241", 10);

if (!seedPath) {
  throw new Error("--seed is required");
}

const seed = JSON.parse(await readFile(seedPath, "utf8"));
await mkdir(outDir, { recursive: true });
await rm(join(outDir, "chrome-profile"), { force: true, recursive: true });

const chrome = spawn(
  chromePath,
  [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${join(outDir, "chrome-profile")}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=1440,900",
    "about:blank",
  ],
  { stdio: "ignore", windowsHide: true },
);

try {
  await waitForChrome(port);
  const target = await createTarget(port);
  const cdp = await CdpClient.connect(target.webSocketDebuggerUrl);
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source: `
      localStorage.setItem("caragent.workbench.workspaceId", ${JSON.stringify(seed.workspace_id)});
      localStorage.setItem("caragent.workbench.briefId", ${JSON.stringify(seed.brief_id)});
    `,
  });

  const captures = [];
  captures.push(
    await captureView(cdp, {
      file: "phase20-v3-desktop-2d-preflight.png",
      label: "desktop-2d-preflight",
      mobile: false,
      width: 1440,
      height: 900,
      setup: async () => {
        await clickButton(cdp, "ZIP");
      },
    }),
  );
  captures.push(
    await captureView(cdp, {
      file: "phase20-v3-desktop-3d-fallback.png",
      label: "desktop-3d-fallback",
      mobile: false,
      width: 1440,
      height: 900,
      setup: async () => {
        await clickButton(cdp, "3D 预览");
      },
    }),
  );
  captures.push(
    await captureView(cdp, {
      file: "phase20-v3-mobile-2d-preflight.png",
      label: "mobile-2d-preflight",
      mobile: true,
      width: 390,
      height: 900,
      setup: async () => {
        await clickButton(cdp, "ZIP");
      },
    }),
  );
  captures.push(
    await captureView(cdp, {
      file: "phase20-v3-mobile-3d-fallback.png",
      label: "mobile-3d-fallback",
      mobile: true,
      width: 390,
      height: 900,
      setup: async () => {
        await clickButton(cdp, "3D 预览");
      },
    }),
  );

  await writeFile(
    join(outDir, "phase20-browser-metrics.json"),
    JSON.stringify(
      {
        driver: `Headless Chrome CDP on 127.0.0.1:${port}`,
        generatedAt: new Date().toISOString(),
        seed,
        url,
        views: captures,
      },
      null,
      2,
    ),
    "utf8",
  );
  await cdp.close();
} finally {
  chrome.kill();
}

async function captureView(cdp, options) {
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    deviceScaleFactor: options.mobile ? 2 : 1,
    height: options.height,
    mobile: options.mobile,
    width: options.width,
  });
  await cdp.send("Page.navigate", { url });
  await waitForSignal(cdp, "Phase 20 V3 UAT ready version");
  await options.setup();
  await wait(700);
  const metrics = await pageMetrics(cdp);
  const screenshot = await cdp.send("Page.captureScreenshot", {
    captureBeyondViewport: true,
    format: "png",
    fromSurface: true,
  });
  await writeFile(join(outDir, options.file), Buffer.from(screenshot.data, "base64"));
  return {
    clientWidth: metrics.clientWidth,
    file: join(outDir, options.file),
    horizontalOverflow: metrics.horizontalOverflow,
    label: options.label,
    maxScrollWidth: metrics.maxScrollWidth,
    signals: metrics.signals,
    textSample: metrics.textSample,
    viewport: `${options.width}x${options.height}${options.mobile ? "@2x" : ""}`,
  };
}

async function pageMetrics(cdp) {
  const result = await cdp.send("Runtime.evaluate", {
    awaitPromise: true,
    returnByValue: true,
    expression: `(() => {
      const text = document.body.innerText;
      const clientWidth = document.documentElement.clientWidth;
      const maxScrollWidth = Math.max(
        document.documentElement.scrollWidth,
        document.body.scrollWidth,
        ...Array.from(document.querySelectorAll("*")).map((node) => node.scrollWidth || 0)
      );
      const includes = (needle) => text.includes(needle);
      return {
        clientWidth,
        maxScrollWidth,
        horizontalOverflow: maxScrollWidth > clientWidth + 1,
        signals: {
          templateCatalog: includes("generic_van_side_v1") && includes("internal_original"),
          templatePreviewSpec: includes("Phase 20 V3 concept preview") && includes("generic_van_side_v1"),
          targetedEdit: includes("局部编辑"),
          threeDFallback: includes("当前模板暂无 3D 壳体，继续使用 2D 预览。"),
          enhancedHandoff: includes("production-readiness-preflight.json") && includes("template-validation.json"),
          preflight: includes("生产预检") && includes("缺少生产证据"),
          conceptOnly: includes("概念预检") || includes("非生产贴膜参考")
        },
        textSample: text.slice(0, 5000)
      };
    })()`,
  });
  return result.result.value;
}

async function clickButton(cdp, label) {
  await cdp.send("Runtime.evaluate", {
    expression: `
      (() => {
        const button = Array.from(document.querySelectorAll("button"))
          .find((candidate) => candidate.textContent && candidate.textContent.includes(${JSON.stringify(label)}));
        if (button) button.click();
      })()
    `,
  });
}

async function waitForSignal(cdp, signal) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const result = await cdp.send("Runtime.evaluate", {
      returnByValue: true,
      expression: `document.body && document.body.innerText.includes(${JSON.stringify(signal)})`,
    });
    if (result.result.value === true) {
      return;
    }
    await wait(250);
  }
  throw new Error(`Timed out waiting for page signal: ${signal}`);
}

async function createTarget(port) {
  const response = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, {
    method: "PUT",
  });
  if (!response.ok) {
    throw new Error(`Failed to create Chrome target: HTTP ${response.status}`);
  }
  return response.json();
}

async function waitForChrome(port) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) {
        return;
      }
    } catch {
      // Keep polling.
    }
    await wait(250);
  }
  throw new Error("Timed out waiting for Chrome remote debugging endpoint");
}

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
