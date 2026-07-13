#!/usr/bin/env node
/**
 * GitHub push webhook → run scripts/deploy.sh
 * Listens on 127.0.0.1 only; nginx proxies /hooks/deploy here.
 */
const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const path = require("path");
const { spawn } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const ENV_FILE = path.join(__dirname, "deploy-webhook.env");
const DEPLOY_SCRIPT = path.join(__dirname, "deploy.sh");
const HOST = process.env.DEPLOY_WEBHOOK_HOST || "127.0.0.1";
const PORT = Number(process.env.DEPLOY_WEBHOOK_PORT || 19082);
const DEPLOY_BRANCH = process.env.DEPLOY_BRANCH || "main";

loadEnv(ENV_FILE);

const SECRET = process.env.GITHUB_WEBHOOK_SECRET;
if (!SECRET) {
  console.error(`Missing GITHUB_WEBHOOK_SECRET in ${ENV_FILE}`);
  process.exit(1);
}

let deployRunning = false;

const server = http.createServer(async (req, res) => {
  const pathname = (req.url || "").split("?")[0];
  if (req.method !== "POST" || pathname !== "/hooks/deploy") {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not found");
    return;
  }

  let body;
  try {
    body = await readBody(req);
  } catch (error) {
    console.warn("[deploy-webhook] failed to read body:", error);
    res.writeHead(400, { "Content-Type": "text/plain" });
    res.end("Bad request");
    return;
  }

  const signature = req.headers["x-hub-signature-256"];
  if (!verifySignature(body, signature, SECRET)) {
    console.warn("[deploy-webhook] invalid signature");
    res.writeHead(401, { "Content-Type": "text/plain" });
    res.end("Unauthorized");
    return;
  }

  const event = req.headers["x-github-event"];
  if (event === "ping") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, message: "pong" }));
    return;
  }

  if (event !== "push") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, ignored: true, event }));
    return;
  }

  let payload;
  try {
    payload = parseGithubPayload(body, req.headers["content-type"]);
  } catch (error) {
    console.warn("[deploy-webhook] invalid payload:", error.message);
    res.writeHead(400, { "Content-Type": "text/plain" });
    res.end("Invalid payload");
    return;
  }

  const ref = payload.ref || "";
  const expectedRef = `refs/heads/${DEPLOY_BRANCH}`;
  if (ref !== expectedRef) {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, ignored: true, ref }));
    return;
  }

  if (deployRunning) {
    res.writeHead(409, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: false, error: "deploy already running" }));
    return;
  }

  deployRunning = true;
  res.writeHead(202, { "Content-Type": "application/json" });
  res.end(
    JSON.stringify({
      ok: true,
      message: "deploy started",
      commit: payload.after,
      branch: DEPLOY_BRANCH,
    }),
  );

  console.log(
    `[deploy-webhook] push to ${DEPLOY_BRANCH}: ${payload.after?.slice(0, 7) || "unknown"}`,
  );

  const child = spawn(DEPLOY_SCRIPT, {
    cwd: ROOT,
    env: {
      ...process.env,
      DEPLOY_BRANCH,
      PATH: `/root/.nvm/versions/node/v22.14.0/bin:${process.env.PATH || ""}`,
    },
    stdio: ["ignore", "pipe", "pipe"],
    detached: false,
  });

  child.stdout.on("data", (chunk) => process.stdout.write(chunk));
  child.stderr.on("data", (chunk) => process.stderr.write(chunk));
  child.on("close", (code) => {
    deployRunning = false;
    if (code === 0) {
      console.log("[deploy-webhook] deploy finished successfully");
    } else {
      console.error(`[deploy-webhook] deploy failed with exit code ${code}`);
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`[deploy-webhook] listening on http://${HOST}:${PORT}/hooks/deploy`);
});

function loadEnv(filePath) {
  if (!fs.existsSync(filePath)) {
    return;
  }
  for (const line of fs.readFileSync(filePath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const eq = trimmed.indexOf("=");
    if (eq === -1) {
      continue;
    }
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) {
      process.env[key] = value;
    }
  }
}

function parseGithubPayload(body, contentTypeHeader) {
  const contentType = String(contentTypeHeader || "").toLowerCase();

  if (contentType.includes("application/x-www-form-urlencoded")) {
    const params = new URLSearchParams(body.toString("utf8"));
    const payload = params.get("payload");
    if (!payload) {
      throw new Error("missing payload field");
    }
    return JSON.parse(payload);
  }

  return JSON.parse(body.toString("utf8"));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

function verifySignature(body, signatureHeader, secret) {
  if (!signatureHeader || typeof signatureHeader !== "string") {
    return false;
  }
  const expected =
    "sha256=" + crypto.createHmac("sha256", secret).update(body).digest("hex");
  const expectedBuf = Buffer.from(expected);
  const actualBuf = Buffer.from(signatureHeader);
  if (expectedBuf.length !== actualBuf.length) {
    return false;
  }
  return crypto.timingSafeEqual(expectedBuf, actualBuf);
}
