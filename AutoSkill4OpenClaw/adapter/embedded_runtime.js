import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

function asString(v) {
  if (v == null) return "";
  return String(v);
}

function trimmed(v) {
  return asString(v).trim();
}

function asBool(v, defaultValue = false) {
  if (v == null) return Boolean(defaultValue);
  if (typeof v === "boolean") return v;
  const s = trimmed(v).toLowerCase();
  if (!s) return Boolean(defaultValue);
  if (["1", "true", "yes", "y", "on"].includes(s)) return true;
  if (["0", "false", "no", "n", "off"].includes(s)) return false;
  return Boolean(defaultValue);
}

function slug(v, fallback = "item") {
  const s = trimmed(v)
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9_.@:-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
  return (s || fallback).slice(0, 96);
}

function nowMs() {
  return Date.now();
}

function jsonDump(v) {
  return JSON.stringify(v, null, 2);
}

function parseJsonLoose(text) {
  const raw = trimmed(text);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (_) {
    const m = raw.match(/\{[\s\S]*\}/);
    if (!m) return null;
    try {
      return JSON.parse(m[0]);
    } catch (_) {
      return null;
    }
  }
}

const MODULE_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_PROMPT_PACK_PATH = path.join(MODULE_DIR, "openclaw_prompt_pack.txt");
const PROMPT_TOKEN_RE = /\{\{([a-zA-Z0-9_.:-]+)\}\}/g;

function parsePromptPack(raw) {
  const blocks = {};
  const templates = {};
  let version = "";
  let mode = "";
  let name = "";
  let buf = [];
  for (const line of String(raw || "").split(/\r?\n/)) {
    const stripped = line.trim();
    if (!mode && stripped.startsWith("@@version ")) {
      version = stripped.slice("@@version ".length).trim();
      continue;
    }
    if (!mode && stripped.startsWith("@@block ")) {
      mode = "block";
      name = stripped.slice("@@block ".length).trim();
      buf = [];
      continue;
    }
    if (!mode && stripped.startsWith("@@template ")) {
      mode = "template";
      name = stripped.slice("@@template ".length).trim();
      buf = [];
      continue;
    }
    if (mode && stripped === "@@end") {
      const text = buf.join("\n").replace(/^\n+|\n+$/g, "");
      if (mode === "block" && name) blocks[name] = text;
      if (mode === "template" && name) templates[name] = text;
      mode = "";
      name = "";
      buf = [];
      continue;
    }
    if (mode) buf.push(line);
  }
  return { version, blocks, templates };
}

function resolvePromptPackPath(cfg) {
  const explicit = trimmed(cfg?.embedded?.promptPackPath);
  if (explicit) return path.resolve(explicit);
  const env = (typeof process !== "undefined" && process && process.env) ? process.env : {};
  const envPath = trimmed(env.AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH);
  if (envPath) return path.resolve(envPath);
  return path.resolve(DEFAULT_PROMPT_PACK_PATH);
}

function loadPromptPack(cfg, log) {
  const p = resolvePromptPackPath(cfg);
  try {
    const raw = fs.readFileSync(p, "utf8");
    const pack = parsePromptPack(raw);
    if (!pack || typeof pack !== "object" || !pack.templates || !pack.blocks) {
      return null;
    }
    if (log && typeof log.info === "function") {
      const version = trimmed(pack.version) || "unknown";
      log.info(`[autoskill-openclaw] embedded prompt pack loaded version=${version} path=${p}`);
    }
    return pack;
  } catch (err) {
    const msg = sanitizeModelCallError(err, "prompt_pack_unavailable");
    if (log && typeof log.info === "function") {
      log.info(`[autoskill-openclaw] embedded prompt pack fallback path=${p} reason=${msg}`);
    }
    return null;
  }
}

function renderPromptText(text, blocks, vars, depth = 0) {
  if (depth > 12) return asString(text);
  return asString(text).replace(PROMPT_TOKEN_RE, (_full, tokenRaw) => {
    const token = trimmed(tokenRaw);
    if (!token) return "";
    if (token.startsWith("var.")) {
      const key = token.slice("var.".length);
      return asString(vars?.[key]);
    }
    if (token.startsWith("block.")) {
      const key = token.slice("block.".length);
      const block = blocks && typeof blocks === "object" ? blocks[key] : "";
      return renderPromptText(block || "", blocks, vars, depth + 1);
    }
    return `{{${token}}}`;
  });
}

function sharedPrompt(pack, key, fallback, vars = {}) {
  const template = pack?.templates?.[key];
  if (!trimmed(template)) return asString(fallback);
  try {
    const rendered = renderPromptText(template, pack?.blocks || {}, vars || {}, 0);
    return trimmed(rendered) ? rendered : asString(fallback);
  } catch (_) {
    return asString(fallback);
  }
}

function collectText(content) {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (typeof item === "string") return item;
        if (!item || typeof item !== "object") return "";
        return asString(item.text || item.content);
      })
      .join("");
  }
  if (content && typeof content === "object") {
    return asString(content.text || content.content);
  }
  return asString(content);
}

function modelTextFromResponse(res) {
  if (typeof res === "string") return trimmed(res);
  if (!res || typeof res !== "object") return "";
  const nested = [res.result, res.response, res.data, res.output, res.final];
  for (const item of nested) {
    const nestedText = modelTextFromResponse(item);
    if (nestedText) return nestedText;
  }
  const direct = trimmed(res.output_text || res.text || res.content);
  if (direct) return direct;
  const msg = res.message;
  if (msg && typeof msg === "object") {
    const content = trimmed(collectText(msg.content));
    if (content) return content;
  }
  const choices = Array.isArray(res.choices) ? res.choices : [];
  for (const c of choices) {
    if (!c || typeof c !== "object") continue;
    const m = c.message || c.delta;
    if (!m || typeof m !== "object") continue;
    const content = trimmed(collectText(m.content));
    if (content) return content;
  }
  return "";
}

function makeMessages(system, user) {
  return [
    { role: "system", content: asString(system) },
    { role: "user", content: asString(user) },
  ];
}

function withTimeout(ms) {
  const controller = new AbortController();
  const timeout = Math.max(1000, Number(ms) || 20000);
  const timer = setTimeout(() => controller.abort(), timeout);
  return { controller, timer };
}

async function nodeHttpFetch(url, opts) {
  const target = new URL(url);
  const isHttps = target.protocol === "https:";
  const mod = await import(isHttps ? "node:https" : "node:http");
  const requestFn = mod.request;
  return await new Promise((resolve, reject) => {
    const req = requestFn(
      {
        method: opts.method || "GET",
        hostname: target.hostname,
        port: target.port || (isHttps ? 443 : 80),
        path: `${target.pathname}${target.search}`,
        headers: opts.headers || {},
      },
      (res) => {
        const chunks = [];
        res.on("data", (c) => chunks.push(Buffer.isBuffer(c) ? c : Buffer.from(String(c))));
        res.on("end", () => {
          const body = Buffer.concat(chunks).toString("utf8");
          const status = Number(res.statusCode) || 0;
          resolve({
            ok: status >= 200 && status < 300,
            status,
            text: async () => body,
          });
        });
      },
    );
    req.on("error", reject);
    if (opts.signal) {
      opts.signal.addEventListener("abort", () => {
        req.destroy(new Error("aborted"));
      });
    }
    if (opts.body) req.write(opts.body);
    req.end();
  });
}

async function requestJson(url, opts) {
  if (typeof fetch === "function") {
    return fetch(url, opts);
  }
  return nodeHttpFetch(url, opts);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normalizeBaseUrl(value) {
  return trimmed(value).replace(/\/+$/, "");
}

function buildChatCompletionsUrl(baseUrl) {
  const base = normalizeBaseUrl(baseUrl);
  if (!base) return "";
  if (/\/chat\/completions$/i.test(base)) return base;
  if (/\/v1$/i.test(base)) return `${base}/chat/completions`;
  return `${base}/v1/chat/completions`;
}

function resolveEnvReference(value) {
  const raw = trimmed(value);
  if (!raw) return "";
  const env = (typeof process !== "undefined" && process && process.env) ? process.env : {};
  const m1 = raw.match(/^\$\{([A-Z0-9_]+)\}$/i);
  if (m1) return trimmed(env[m1[1]]);
  const m2 = raw.match(/^\$([A-Z0-9_]+)$/i);
  if (m2) return trimmed(env[m2[1]]);
  const m3 = raw.match(/^env:([A-Z0-9_]+)$/i);
  if (m3) return trimmed(env[m3[1]]);
  return raw;
}

function sanitizeModelCallError(err, fallback = "request_failed") {
  const text = trimmed(err && err.message ? err.message : err);
  if (!text) return fallback;
  return text.slice(0, 280);
}

function envKeysFromProvider(provider) {
  const p = trimmed(provider)
    .replace(/[^a-zA-Z0-9]/g, "_")
    .toUpperCase();
  if (!p) return [];
  return [`${p}_API_KEY`, `${p}_KEY`, `${p}_TOKEN`, `${p}_BASE_URL`, `${p}_MODEL`];
}

function resolveEnvKeyValue(explicitName, provider, suffix) {
  const env = (typeof process !== "undefined" && process && process.env) ? process.env : {};
  const names = [];
  const explicit = trimmed(resolveEnvReference(explicitName));
  if (explicit && /^[A-Z0-9_]+$/i.test(explicit)) names.push(explicit);
  const providerNames = envKeysFromProvider(provider);
  for (const key of providerNames) {
    if (key.endsWith(`_${suffix}`)) names.push(key);
  }
  if (suffix === "API_KEY") {
    names.push(
      "OPENAI_API_KEY",
      "ANTHROPIC_API_KEY",
      "DASHSCOPE_API_KEY",
      "QWEN_API_KEY",
      "INTERNLM_API_KEY",
      "DEEPSEEK_API_KEY",
      "GEMINI_API_KEY",
      "GOOGLE_API_KEY",
    );
  } else if (suffix === "BASE_URL") {
    names.push("OPENAI_BASE_URL");
  } else if (suffix === "MODEL") {
    names.push("OPENAI_MODEL");
  }
  for (const name of names) {
    const v = trimmed(env[name]);
    if (v) return v;
  }
  return "";
}

function collectFunctionProbes(containers, names) {
  const probes = [];
  for (const obj of containers) {
    if (!obj || typeof obj !== "object") continue;
    for (const name of names) {
      if (typeof obj[name] === "function") {
        probes.push(obj[name].bind(obj));
      }
    }
  }
  return probes;
}

function createRuntimeDirectInvoker(api) {
  const containers = [api, api?.runtime, api?.model, api?.runtime?.model, api?.llm, api?.services];
  const names = ["invokeModel", "callModel", "chatCompletion", "createChatCompletion", "runModel", "complete"];
  const probes = collectFunctionProbes(containers, names);
  return async ({ system, user, model, metadata }) => {
    if (!probes.length) {
      throw new Error("openclaw_runtime_not_available");
    }
    const errors = [];
    for (const fn of probes) {
      const payloads = [
        {
          model,
          messages: makeMessages(system, user),
          temperature: 0,
          metadata,
        },
        {
          model,
          system,
          user,
          temperature: 0,
          metadata,
        },
      ];
      for (const payload of payloads) {
        try {
          const out = await fn(payload);
          const text = modelTextFromResponse(out);
          if (text) return text;
        } catch (err) {
          errors.push(sanitizeModelCallError(err));
        }
      }
    }
    throw new Error(`openclaw_runtime_failed:${errors.join("|")}`);
  };
}

function createRuntimeSubagentInvoker(api) {
  const containers = [
    api,
    api?.runtime,
    api?.agent,
    api?.runtime?.agent,
    api?.subAgent,
    api?.subagent,
    api?.agents,
  ];
  const names = [
    "runSubAgent",
    "invokeSubAgent",
    "callSubAgent",
    "runAgent",
    "invokeAgent",
    "spawnAgent",
    "createSubAgent",
  ];
  const probes = collectFunctionProbes(containers, names);
  return async ({ system, user, model, metadata }) => {
    if (!probes.length) {
      throw new Error("openclaw_runtime_subagent_not_available");
    }
    const errors = [];
    for (const fn of probes) {
      const payloads = [
        {
          model,
          systemPrompt: system,
          userPrompt: user,
          prompt: user,
          task: user,
          input: user,
          metadata,
          autoskill_internal: true,
        },
        {
          system,
          user,
          model,
          metadata,
          autoskill_internal: true,
        },
      ];
      const variants = [
        ...payloads.map((payload) => ({ kind: "object", payload })),
        {
          kind: "args",
          args: [
            user,
            {
              system,
              model,
              metadata,
              autoskill_internal: true,
            },
          ],
        },
      ];
      for (const variant of variants) {
        try {
          const out = variant.kind === "args" ? await fn(...variant.args) : await fn(variant.payload);
          const text = modelTextFromResponse(out);
          if (text) return text;
        } catch (err) {
          errors.push(sanitizeModelCallError(err));
        }
      }
    }
    throw new Error(`openclaw_runtime_subagent_failed:${errors.join("|")}`);
  };
}

function pickString(obj, keys) {
  if (!obj || typeof obj !== "object") return "";
  for (const key of keys) {
    if (!Object.prototype.hasOwnProperty.call(obj, key)) continue;
    const value = trimmed(obj[key]);
    if (value) return value;
  }
  return "";
}

function providerFromPath(pathSegments) {
  const segs = Array.isArray(pathSegments) ? pathSegments : [];
  for (let i = 0; i < segs.length; i += 1) {
    if (segs[i] !== "providers") continue;
    const p = trimmed(segs[i + 1]);
    if (p) return p;
  }
  return "";
}

function looksLikeConfigFile(filePath) {
  const base = path.basename(filePath).toLowerCase();
  return ["openclaw.json", "config.json", "models.json", "model.json", "providers.json"].includes(base);
}

function discoverConfigFiles(openclawHome) {
  const root = path.resolve(openclawHome || "");
  if (!root || !fs.existsSync(root)) return [];
  const out = [];
  const seen = new Set();
  const pushIfFile = (filePath) => {
    const p = path.resolve(filePath);
    if (seen.has(p)) return;
    if (!fs.existsSync(p)) return;
    try {
      if (!fs.statSync(p).isFile()) return;
    } catch (_) {
      return;
    }
    seen.add(p);
    out.push(p);
  };
  for (const name of ["openclaw.json", "config.json", "models.json", "model.json", "providers.json"]) {
    pushIfFile(path.join(root, name));
    pushIfFile(path.join(root, "workspace", name));
    pushIfFile(path.join(root, "config", name));
    pushIfFile(path.join(root, "workspace", "config", name));
  }
  for (const dir of [path.join(root, "agents"), path.join(root, "workspace", "agents")]) {
    if (!fs.existsSync(dir)) continue;
    let entries = [];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch (_) {
      entries = [];
    }
    for (const entry of entries) {
      if (!entry || !entry.isDirectory()) continue;
      pushIfFile(path.join(dir, entry.name, "models.json"));
      pushIfFile(path.join(dir, entry.name, "model.json"));
      pushIfFile(path.join(dir, entry.name, "openclaw.json"));
      pushIfFile(path.join(dir, entry.name, "config.json"));
    }
  }
  const queue = [{ dir: root, depth: 0 }];
  const maxDepth = 2;
  while (queue.length) {
    const current = queue.shift();
    if (!current) break;
    let entries = [];
    try {
      entries = fs.readdirSync(current.dir, { withFileTypes: true });
    } catch (_) {
      entries = [];
    }
    for (const entry of entries) {
      const nextPath = path.join(current.dir, entry.name);
      if (entry.isFile() && looksLikeConfigFile(nextPath)) {
        pushIfFile(nextPath);
      } else if (entry.isDirectory() && current.depth < maxDepth) {
        queue.push({ dir: nextPath, depth: current.depth + 1 });
      }
    }
  }
  return out;
}

function readJsonSafe(filePath) {
  try {
    const raw = fs.readFileSync(filePath, "utf8");
    const obj = JSON.parse(raw);
    if (obj && typeof obj === "object") return obj;
    return null;
  } catch (_) {
    return null;
  }
}

function resolveConfigTargetFromFile(filePath, modelHint) {
  const root = readJsonSafe(filePath);
  if (!root) return null;
  const baseKeys = ["base_url", "baseUrl", "api_base", "apiBase", "endpoint", "url"];
  const modelKeys = ["model", "model_id", "modelId", "default_model", "defaultModel", "chat_model", "chatModel"];
  const keyKeys = ["api_key", "apiKey", "key", "token", "access_token", "accessToken"];
  const keyEnvKeys = ["api_key_env", "apiKeyEnv", "keyEnv", "token_env", "tokenEnv", "api_key_ref", "apiKeyRef"];
  const providerKeys = ["provider", "provider_id", "providerId", "name"];
  const baseEnvKeys = ["base_url_env", "baseUrlEnv"];
  const modelEnvKeys = ["model_env", "modelEnv"];
  const activeProvider =
    pickString(root, ["active_provider", "activeProvider", "current_provider", "currentProvider", "provider"]) ||
    pickString(root?.llm, ["provider", "active_provider", "activeProvider"]);
  const activeModel =
    pickString(root, ["active_model", "activeModel", "current_model", "currentModel", "model"]) ||
    pickString(root?.llm, ["model", "default_model", "defaultModel"]);
  const nodes = [];
  const stack = [{ value: root, path: [], depth: 0 }];
  while (stack.length) {
    const item = stack.pop();
    if (!item || !item.value || typeof item.value !== "object") continue;
    const value = item.value;
    if (item.depth > 6) continue;
    const baseUrl = pickString(value, baseKeys);
    const provider = pickString(value, providerKeys) || providerFromPath(item.path) || activeProvider;
    const explicitApiKey = resolveEnvReference(pickString(value, keyKeys));
    const explicitApiKeyEnv = pickString(value, keyEnvKeys);
    const explicitBaseEnv = pickString(value, baseEnvKeys);
    const explicitModelEnv = pickString(value, modelEnvKeys);
    const modelValue = pickString(value, modelKeys);
    const resolvedApiKey =
      explicitApiKey ||
      resolveEnvKeyValue(explicitApiKeyEnv, provider, "API_KEY");
    const resolvedBaseUrl =
      normalizeBaseUrl(resolveEnvReference(baseUrl || resolveEnvKeyValue(explicitBaseEnv, provider, "BASE_URL")));
    const resolvedModel =
      trimmed(resolveEnvReference(modelValue || resolveEnvKeyValue(explicitModelEnv, provider, "MODEL"))) ||
      trimmed(modelHint) ||
      activeModel;
    if (resolvedBaseUrl) {
      let score = 10;
      if (resolvedModel) score += 2;
      if (resolvedApiKey) score += 1;
      if (activeProvider && provider && trimmed(activeProvider).toLowerCase() === trimmed(provider).toLowerCase()) {
        score += 2;
      }
      if (activeModel && resolvedModel && trimmed(activeModel).toLowerCase() === trimmed(resolvedModel).toLowerCase()) {
        score += 2;
      }
      if (modelHint && resolvedModel && trimmed(modelHint).toLowerCase() === trimmed(resolvedModel).toLowerCase()) {
        score += 3;
      }
      nodes.push({
        score,
        baseUrl: resolvedBaseUrl,
        model: resolvedModel,
        apiKey: resolvedApiKey,
        provider: provider || activeProvider,
      });
    }
    const entries = Object.entries(value);
    for (const [key, child] of entries) {
      if (!child || typeof child !== "object") continue;
      stack.push({ value: child, path: item.path.concat(key), depth: item.depth + 1 });
    }
  }
  if (!nodes.length) return null;
  nodes.sort((a, b) => b.score - a.score);
  return { ...nodes[0], source: filePath };
}

function resolveConfigTarget(cfg, modelHint) {
  const invocationCfg = cfg?.embedded?.modelInvocation || {};
  const openclawHome = trimmed(invocationCfg.openclawHome) || trimmed(cfg?.embedded?.openclawHome);
  if (!openclawHome) return null;
  const files = discoverConfigFiles(openclawHome);
  if (!files.length) return null;
  const targets = [];
  for (const filePath of files) {
    const target = resolveConfigTargetFromFile(filePath, modelHint);
    if (target && target.baseUrl) targets.push(target);
  }
  if (!targets.length) return null;
  targets.sort((a, b) => b.score - a.score);
  const best = targets[0];
  return {
    baseUrl: best.baseUrl,
    apiKey: best.apiKey || "",
    model: best.model || trimmed(modelHint),
    provider: best.provider || "",
    source: best.source || "",
  };
}

function resolveRuntimeTarget(api, modelHint) {
  const containers = [api, api?.runtime, api?.model, api?.runtime?.model, api?.provider, api?.runtime?.provider];
  const baseKeys = ["base_url", "baseUrl", "api_base", "apiBase", "endpoint", "url"];
  const modelKeys = ["model", "model_id", "modelId", "default_model", "defaultModel", "chat_model", "chatModel"];
  const keyKeys = ["api_key", "apiKey", "key", "token", "access_token", "accessToken"];
  const keyEnvKeys = ["api_key_env", "apiKeyEnv", "keyEnv", "token_env", "tokenEnv"];
  const baseEnvKeys = ["base_url_env", "baseUrlEnv"];
  const modelEnvKeys = ["model_env", "modelEnv"];
  const providerKeys = ["provider", "provider_id", "providerId", "name"];
  const candidates = [];
  for (const root of containers) {
    if (!root || typeof root !== "object") continue;
    const stack = [{ value: root, depth: 0 }];
    const seen = new Set();
    while (stack.length) {
      const item = stack.pop();
      if (!item || !item.value || typeof item.value !== "object") continue;
      const value = item.value;
      if (item.depth > 4) continue;
      if (seen.has(value)) continue;
      seen.add(value);
      const provider = pickString(value, providerKeys);
      const baseUrl = normalizeBaseUrl(
        resolveEnvReference(
          pickString(value, baseKeys) || resolveEnvKeyValue(pickString(value, baseEnvKeys), provider, "BASE_URL"),
        ),
      );
      const model =
        trimmed(
          resolveEnvReference(
            pickString(value, modelKeys) || resolveEnvKeyValue(pickString(value, modelEnvKeys), provider, "MODEL"),
          ),
        ) ||
        trimmed(modelHint);
      const apiKey =
        trimmed(resolveEnvReference(pickString(value, keyKeys))) ||
        resolveEnvKeyValue(pickString(value, keyEnvKeys), provider, "API_KEY");
      if (baseUrl) {
        let score = 10;
        if (model) score += 2;
        if (apiKey) score += 1;
        if (modelHint && model && trimmed(modelHint).toLowerCase() === model.toLowerCase()) score += 2;
        candidates.push({ score, baseUrl, model, apiKey, provider });
      }
      for (const child of Object.values(value)) {
        if (child && typeof child === "object") {
          stack.push({ value: child, depth: item.depth + 1 });
        }
      }
    }
  }
  if (!candidates.length) return null;
  candidates.sort((a, b) => b.score - a.score);
  const best = candidates[0];
  return {
    baseUrl: best.baseUrl,
    apiKey: best.apiKey || "",
    model: best.model || trimmed(modelHint),
    provider: best.provider || "",
  };
}

async function callOpenAICompatible(target, request, invokeCfg, requestFn) {
  const model = trimmed(request.model || target.model);
  if (!model) {
    throw new Error("model_missing");
  }
  const url = buildChatCompletionsUrl(target.baseUrl);
  if (!url) {
    throw new Error("base_url_missing");
  }
  const body = JSON.stringify({
    model,
    messages: makeMessages(request.system, request.user),
    temperature: 0,
    metadata: request.metadata,
  });
  const retries = Math.max(0, Number(invokeCfg?.retries) || 0);
  const timeoutMs = Math.max(1000, Number(invokeCfg?.timeoutMs) || 20000);
  let lastError = null;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    const { controller, timer } = withTimeout(timeoutMs);
    try {
      const headers = { "Content-Type": "application/json" };
      if (trimmed(target.apiKey)) {
        headers.Authorization = `Bearer ${target.apiKey}`;
      }
      const res = await requestFn(url, {
        method: "POST",
        headers,
        body,
        signal: controller.signal,
      });
      const text = await res.text();
      const parsed = parseJsonLoose(text);
      if (!res.ok) {
        const errText = trimmed(parsed?.error?.message || text || `HTTP ${res.status}`);
        throw new Error(errText.slice(0, 280));
      }
      const modelText = modelTextFromResponse(parsed || text);
      if (modelText) return modelText;
      throw new Error("empty_model_response");
    } catch (err) {
      lastError = err;
      if (attempt < retries) {
        await sleep(120 * (attempt + 1));
      }
    } finally {
      clearTimeout(timer);
    }
  }
  throw new Error(sanitizeModelCallError(lastError, "request_failed"));
}

function normalizeInvocationModes(modesInput) {
  const defaults = [
    "openclaw-runtime",
    "openclaw-runtime-subagent",
    "openclaw-config-resolve",
    "manual",
  ];
  const source = Array.isArray(modesInput) ? modesInput : defaults;
  const out = [];
  const seen = new Set();
  for (const raw of source) {
    const mode = trimmed(raw).toLowerCase();
    if (!mode) continue;
    if (!["openclaw-runtime", "openclaw-runtime-subagent", "openclaw-config-resolve", "manual"].includes(mode)) {
      continue;
    }
    if (seen.has(mode)) continue;
    seen.add(mode);
    out.push(mode);
  }
  return out.length ? out : defaults;
}

function createDefaultModelInvoker(cfg, api, log, deps = {}) {
  const invocationCfg = cfg?.embedded?.modelInvocation || {};
  const requestFn = typeof deps.requestJson === "function" ? deps.requestJson : requestJson;
  const directRuntimeInvoker = createRuntimeDirectInvoker(api);
  const subagentInvoker = createRuntimeSubagentInvoker(api);
  let cachedRuntimeTarget = null;
  let runtimeResolvedAt = 0;
  let cachedConfigTarget = null;
  let configResolvedAt = 0;

  const modeToInvoker = {
    "openclaw-runtime": async (request) => {
      let lastRuntimeErr = null;
      try {
        return await directRuntimeInvoker(request);
      } catch (err) {
        lastRuntimeErr = err;
      }
      const ttlMs = 30000;
      const now = nowMs();
      if (!cachedRuntimeTarget || now - runtimeResolvedAt > ttlMs) {
        cachedRuntimeTarget = resolveRuntimeTarget(api, request.model || "");
        runtimeResolvedAt = now;
      }
      const target = cachedRuntimeTarget;
      if (!target || !target.baseUrl) {
        throw lastRuntimeErr || new Error("openclaw_runtime_unavailable");
      }
      try {
        return await callOpenAICompatible(
          { ...target, model: trimmed(request.model || target.model) || target.model },
          request,
          invocationCfg,
          requestFn,
        );
      } catch (err) {
        const left = sanitizeModelCallError(lastRuntimeErr, "openclaw_runtime_unavailable");
        const right = sanitizeModelCallError(err);
        throw new Error(`${left}|runtime_target_http:${right}`);
      }
    },
    "openclaw-runtime-subagent": async (request) => subagentInvoker(request),
    "openclaw-config-resolve": async (request) => {
      const ttlMs = 30000;
      const now = nowMs();
      if (!cachedConfigTarget || now - configResolvedAt > ttlMs) {
        cachedConfigTarget = resolveConfigTarget(cfg, request.model || "");
        configResolvedAt = now;
      }
      const target = cachedConfigTarget;
      if (!target || !target.baseUrl) {
        throw new Error("openclaw_config_resolve_unavailable");
      }
      const selectedModel = trimmed(request.model || target.model);
      return callOpenAICompatible(
        { ...target, model: selectedModel || target.model },
        request,
        invocationCfg,
        requestFn,
      );
    },
    manual: async (request) => {
      const target = {
        baseUrl: normalizeBaseUrl(invocationCfg.manualBaseUrl),
        apiKey: trimmed(invocationCfg.manualApiKey),
        model: trimmed(invocationCfg.manualModel || request.model),
      };
      if (!target.baseUrl) {
        throw new Error("manual_not_configured");
      }
      return callOpenAICompatible(target, request, invocationCfg, requestFn);
    },
  };

  const modes = normalizeInvocationModes(invocationCfg.modes);
  return async ({ system, user, model, metadata }) => {
    const errors = [];
    for (const mode of modes) {
      const invoker = modeToInvoker[mode];
      if (typeof invoker !== "function") continue;
      try {
        const text = await invoker({ system, user, model, metadata });
        if (trimmed(text)) return text;
        errors.push(`${mode}:empty_response`);
      } catch (err) {
        errors.push(`${mode}:${sanitizeModelCallError(err)}`);
      }
    }
    if (log?.warn) {
      log.warn(`[autoskill-openclaw-adapter] embedded model call failed across modes: ${errors.join(" | ")}`);
    }
    throw new Error("model_call_failed");
  };
}

function sanitizeMessage(item) {
  if (!item || typeof item !== "object") return null;
  const role = trimmed(item.role).toLowerCase();
  if (!["system", "user", "assistant", "tool"].includes(role)) return null;
  const content = trimmed(collectText(item.content));
  if (!content) return null;
  return { role, content };
}

function sanitizeMessages(list) {
  if (!Array.isArray(list)) return [];
  const out = [];
  for (const item of list) {
    const msg = sanitizeMessage(item);
    if (!msg) continue;
    out.push(msg);
  }
  return out;
}

function mergeMessagesWithOverlap(existing, incoming) {
  const a = Array.isArray(existing) ? existing.slice() : [];
  const b = Array.isArray(incoming) ? incoming.slice() : [];
  if (!a.length) return b;
  if (!b.length) return a;
  let overlap = 0;
  const maxN = Math.min(a.length, b.length);
  for (let n = maxN; n >= 1; n -= 1) {
    const left = a.slice(a.length - n);
    const right = b.slice(0, n);
    if (JSON.stringify(left) === JSON.stringify(right)) {
      overlap = n;
      break;
    }
  }
  return a.concat(b.slice(overlap));
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function appendJsonl(filePath, obj) {
  ensureDir(path.dirname(filePath));
  fs.appendFileSync(filePath, `${JSON.stringify(obj)}\n`, "utf8");
}

function writeJson(filePath, obj) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(obj, null, 2)}\n`, "utf8");
}

function readJsonl(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const lines = fs.readFileSync(filePath, "utf8").split(/\r?\n/);
  const out = [];
  for (const line of lines) {
    const text = trimmed(line);
    if (!text) continue;
    try {
      const obj = JSON.parse(text);
      if (obj && typeof obj === "object") out.push(obj);
    } catch (_) {
      continue;
    }
  }
  return out;
}

function finalizeSessionFile(filePath, reason) {
  if (!fs.existsSync(filePath)) return "";
  const parsed = path.parse(filePath);
  const dst = path.join(parsed.dir, `${parsed.name}.${nowMs()}.${slug(reason, "closed")}${parsed.ext}`);
  try {
    fs.renameSync(filePath, dst);
    return dst;
  } catch (_) {
    return filePath;
  }
}

function finalizeSnapshotFile(filePath, reason) {
  if (!fs.existsSync(filePath)) return "";
  const parsed = path.parse(filePath);
  const dst = path.join(parsed.dir, `${parsed.name}.${nowMs()}.${slug(reason, "closed")}${parsed.ext}`);
  try {
    fs.renameSync(filePath, dst);
    return dst;
  } catch (_) {
    return filePath;
  }
}

function cjkBigrams(text) {
  const chars = Array.from(asString(text || "")).filter((ch) => /[\u3400-\u9FFF]/u.test(ch));
  const out = [];
  for (let i = 0; i < chars.length; i += 1) {
    out.push(chars[i]);
    if (i + 1 < chars.length) out.push(`${chars[i]}${chars[i + 1]}`);
  }
  return out;
}

function tokenize(text) {
  const source = asString(text).toLowerCase();
  const words = source.match(/[\p{L}\p{N}_]+/gu) || [];
  return words.concat(cjkBigrams(source));
}

function bm25Scores(queryText, docs) {
  const k1 = 1.5;
  const b = 0.75;
  const query = tokenize(queryText);
  if (!query.length) return new Map();
  const df = new Map();
  let totalLen = 0;
  for (const doc of docs) {
    const toks = tokenize(doc.text);
    doc._tokens = toks;
    totalLen += toks.length;
    const uniq = new Set(toks);
    for (const t of uniq) {
      df.set(t, (df.get(t) || 0) + 1);
    }
  }
  const avgLen = docs.length ? totalLen / docs.length : 1;
  const scores = new Map();
  for (const doc of docs) {
    const freqs = new Map();
    for (const t of doc._tokens) freqs.set(t, (freqs.get(t) || 0) + 1);
    const dl = Math.max(1, doc._tokens.length);
    let score = 0;
    for (const t of query) {
      const f = freqs.get(t) || 0;
      if (!f) continue;
      const n = df.get(t) || 0;
      const idf = Math.log(1 + (docs.length - n + 0.5) / (n + 0.5));
      const num = f * (k1 + 1);
      const den = f + k1 * (1 - b + b * (dl / avgLen));
      score += idf * (num / den);
    }
    scores.set(doc.id, score);
  }
  return scores;
}

function parseFrontmatter(md) {
  const text = asString(md);
  if (!text.startsWith("---\n")) return {};
  const end = text.indexOf("\n---\n", 4);
  if (end < 0) return {};
  const fm = text.slice(4, end);
  const out = {};
  for (const line of fm.split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
    if (!m) continue;
    out[m[1]] = trimmed(m[2]).replace(/^['"]|['"]$/g, "");
  }
  return out;
}

function parseListFromSection(md, title) {
  const text = asString(md);
  const r = new RegExp(`##\\s+${title}\\s*[\\r\\n]+([\\s\\S]*?)(?:\\n##\\s+|$)`, "i");
  const m = text.match(r);
  if (!m) return [];
  const body = m[1];
  const out = [];
  for (const line of body.split(/\r?\n/)) {
    const mm = line.match(/^\s*-\s+(.+?)\s*$/);
    if (!mm) continue;
    const item = trimmed(mm[1]).replace(/^`|`$/g, "");
    if (item) out.push(item);
  }
  return out;
}

function parsePromptFromSkillMd(md) {
  const text = asString(md);
  const m = text.match(/##\s+Prompt\s*[\r\n]+([\s\S]*?)(?:\n##\s+|$)/i);
  return trimmed(m ? m[1] : text);
}

function clampText(value, maxChars) {
  const text = asString(value);
  const limit = Math.max(16, Number(maxChars) || 0);
  if (!limit || text.length <= limit) return text;
  return text.slice(0, limit).trim();
}

function normalizeComparableText(value) {
  return trimmed(value).replace(/\s+/g, " ").toLowerCase();
}

function normalizeStringList(values, maxItems, maxChars) {
  const src = Array.isArray(values) ? values : [];
  const out = [];
  const seen = new Set();
  for (const item of src) {
    const text = clampText(trimmed(item), maxChars);
    if (!text) continue;
    const key = text.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(text);
    if (out.length >= Math.max(1, Number(maxItems) || 1)) break;
  }
  return out;
}

function normalizeSkillPayload(raw, fallback = {}) {
  const base = raw && typeof raw === "object" ? raw : {};
  const fb = fallback && typeof fallback === "object" ? fallback : {};
  const name = clampText(trimmed(base.name || base.title || fb.name), 96);
  const prompt = clampText(trimmed(base.prompt || base.instructions || fb.prompt || fb.instructions), 6000);
  const description = clampText(trimmed(base.description || base.summary || fb.description || name), 240);
  return {
    name: name || clampText(trimmed(fb.name || "Unnamed Skill"), 96),
    description: description || clampText(trimmed(fb.description || name || "Skill"), 240),
    prompt: prompt || clampText(trimmed(fb.prompt || fb.instructions || ""), 6000),
    triggers: normalizeStringList(base.triggers || fb.triggers, 8, 120),
    tags: normalizeStringList(base.tags || fb.tags, 10, 48),
  };
}

function normalizeDecisionAction(value) {
  const action = trimmed(value).toLowerCase();
  if (["merge", "update", "revise", "refine", "merge_existing", "replace"].includes(action)) {
    return "merge";
  }
  if (["discard", "skip", "ignore", "reject", "none", "drop"].includes(action)) {
    return "discard";
  }
  return "add";
}

function oneLineYamlValue(value, fallback = "") {
  const base = trimmed(value || fallback);
  if (!base) return "";
  return base.replace(/\s+/g, " ").trim();
}

function renderSkillMd(skill, previousId = "", previousVersion = "") {
  const safeName = oneLineYamlValue(skill.name, "Unnamed Skill");
  const safeDescription = oneLineYamlValue(skill.description, safeName);
  const safePrompt = asString(skill.prompt || skill.instructions || "").trim();
  const id = oneLineYamlValue(
    previousId || `skill-${slug(skill.name || skill.description || "unnamed")}-${nowMs()}`,
    `skill-${nowMs()}`,
  );
  const version = oneLineYamlValue(previousVersion || "0.1.0", "0.1.0");
  const tags = Array.isArray(skill.tags)
    ? skill.tags.map((item) => oneLineYamlValue(item)).filter(Boolean)
    : [];
  const triggers = Array.isArray(skill.triggers)
    ? skill.triggers.map((item) => oneLineYamlValue(item)).filter(Boolean)
    : [];
  const lines = [];
  lines.push("---");
  lines.push(`id: "${id}"`);
  lines.push(`name: "${safeName.replace(/"/g, '\\"')}"`);
  lines.push(`description: "${safeDescription.replace(/"/g, '\\"')}"`);
  lines.push(`version: "${version}"`);
  if (tags.length) {
    lines.push("tags:");
    for (const t of tags) lines.push(`  - "${asString(t).replace(/"/g, '\\"')}"`);
  }
  if (triggers.length) {
    lines.push("triggers:");
    for (const t of triggers) lines.push(`  - "${asString(t).replace(/"/g, '\\"')}"`);
  }
  lines.push("---");
  lines.push("");
  lines.push(`# ${safeName}`);
  lines.push("");
  lines.push(safeDescription);
  lines.push("");
  lines.push("## Prompt");
  lines.push("");
  lines.push(safePrompt);
  lines.push("");
  if (triggers.length) {
    lines.push("## Triggers");
    lines.push("");
    for (const t of triggers) lines.push(`- ${t}`);
    lines.push("");
  }
  return lines.join("\n").trimEnd() + "\n";
}

function bumpPatch(version) {
  const m = asString(version).match(/^(\d+)\.(\d+)\.(\d+)$/);
  if (!m) return "0.1.1";
  return `${m[1]}.${m[2]}.${Number(m[3]) + 1}`;
}

function loadUserSkills(skillBankDir, userId) {
  const userRoot = path.join(skillBankDir, "Users", slug(userId || "default", "default"));
  if (!fs.existsSync(userRoot)) return [];
  const dirs = fs.readdirSync(userRoot, { withFileTypes: true }).filter((d) => d.isDirectory());
  const out = [];
  for (const d of dirs) {
    const dirPath = path.join(userRoot, d.name);
    const mdPath = path.join(dirPath, "SKILL.md");
    if (!fs.existsSync(mdPath)) continue;
    const md = fs.readFileSync(mdPath, "utf8");
    const fm = parseFrontmatter(md);
    out.push({
      id: d.name,
      dirName: d.name,
      dirPath,
      mdPath,
      md,
      name: trimmed(fm.name) || d.name,
      description: trimmed(fm.description),
      version: trimmed(fm.version) || "0.1.0",
      parsedId: trimmed(fm.id) || "",
      prompt: parsePromptFromSkillMd(md),
      triggers: parseListFromSection(md, "Triggers"),
      tags: parseListFromSection(md, "Tags"),
      text: `${trimmed(fm.name)}\n${trimmed(fm.description)}\n${parsePromptFromSkillMd(md)}\n${md}`,
    });
  }
  return out;
}

function queryTextFromCandidate(candidate) {
  const triggers = Array.isArray(candidate.triggers) ? candidate.triggers.join("\n") : "";
  const tags = Array.isArray(candidate.tags) ? candidate.tags.join("\n") : "";
  return `${asString(candidate.name)}\n${asString(candidate.description)}\n${asString(candidate.prompt)}\n${triggers}\n${tags}`;
}

function topBm25Hits(candidate, skills, topK) {
  const docs = skills.map((s) => ({ id: s.id, text: s.text }));
  const scores = bm25Scores(queryTextFromCandidate(candidate), docs);
  const ranked = skills
    .map((s) => ({ ...s, score: Number(scores.get(s.id) || 0) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, Math.max(1, Number(topK) || 8));
  return ranked;
}

async function extractCandidate({ invokeModel, sessionMessages, model, metadata, renderSharedPrompt }) {
  const fallbackSystem =
    "You are AutoSkill embedded extractor for OpenClaw sessions. " +
    "Extract at most one reusable skill from the provided session. " +
    "Only extract if reusable and future-facing. Output strict JSON only.";
  const system = renderSharedPrompt("embedded.extract.system", fallbackSystem, { max_candidates: 1 });
  const user = jsonDump({
    schema: {
      skills: [
        {
          name: "string",
          description: "string",
          prompt: "string markdown prompt",
          triggers: ["string"],
          tags: ["string"],
          confidence: 0.0,
        },
      ],
    },
    rules: [
      "Require turn_type=main evidence in session.",
      "Ignore one-off payload.",
      "No examples field.",
      "Keep concise.",
    ],
    session_messages: sessionMessages,
  });
  const text = await invokeModel({ system, user, model, metadata });
  const obj = parseJsonLoose(text);
  const skills = Array.isArray(obj?.skills)
    ? obj.skills
    : obj?.skill && typeof obj.skill === "object"
      ? [obj.skill]
      : obj && typeof obj === "object"
        ? [obj]
        : [];
  if (!skills.length) return null;
  const normalized = normalizeSkillPayload(skills[0] || {});
  if (!normalized.name || !normalized.prompt) return null;
  return normalized;
}

async function decideAction({ invokeModel, candidate, hits, model, metadata, renderSharedPrompt }) {
  const fallbackSystem =
    "You decide skill maintenance action for OpenClaw. Output strict JSON with fields action,target_skill_id,reason.";
  const system = renderSharedPrompt("embedded.maintain.decide.system", fallbackSystem);
  const user = jsonDump({
    candidate,
    similar_skills: hits.map((h) => ({
      id: h.id,
      name: h.name,
      description: h.description,
      score: Number(h.score || 0),
    })),
    rules: [
      "actions: add|merge|discard",
      "merge only when similar_skills contains clear same capability evidence.",
      "for merge, prefer explicit target_skill_id from similar_skills ids.",
      "prefer merge when same capability and candidate improves it",
      "discard generic weak skills",
    ],
  });
  try {
    const text = await invokeModel({ system, user, model, metadata });
    const obj = parseJsonLoose(text) || {};
    const action = normalizeDecisionAction(obj.action || obj.decision || obj.operation);
    const targetRaw = trimmed(obj.target_skill_id || obj.targetSkillId || obj.skill_id || obj.skillId || obj.target);
    if (action === "discard") {
      return { action: "discard", target: "" };
    }
    if (action === "merge") {
      const exact = hits.find((h) => normalizeComparableText(h.id) === normalizeComparableText(targetRaw));
      if (exact) {
        return { action: "merge", target: exact.id };
      }
      const best = hits[0];
      if (best && Number(best.score) >= 0.72) {
        return { action: "merge", target: best.id };
      }
      return { action: "add", target: "" };
    }
    return { action: "add", target: "" };
  } catch (_) {
    // fall through
  }
  const best = hits[0];
  if (best && Number(best.score) >= 0.72) {
    return { action: "merge", target: best.id };
  }
  return { action: "add", target: "" };
}

async function mergeSkillWithModel({ invokeModel, existing, candidate, model, metadata, renderSharedPrompt }) {
  const fallbackSystem =
    "Merge existing skill and candidate skill into one skill. " +
    "Output strict JSON with name,description,prompt,triggers,tags.";
  const system = renderSharedPrompt("embedded.maintain.merge.system", fallbackSystem);
  const user = jsonDump({
    existing: {
      name: existing.name,
      description: existing.description,
      prompt: existing.prompt,
      triggers: existing.triggers,
      tags: existing.tags,
    },
    candidate,
  });
  try {
    const text = await invokeModel({ system, user, model, metadata });
    const obj = parseJsonLoose(text);
    if (obj && typeof obj === "object") {
      return normalizeSkillPayload(obj, existing);
    }
  } catch (_) {
    // fallback heuristic below
  }
  const mergeSet = (a, b, n) => {
    const out = [];
    const seen = new Set();
    for (const v of [...(a || []), ...(b || [])]) {
      const s = trimmed(v);
      if (!s) continue;
      const k = s.toLowerCase();
      if (seen.has(k)) continue;
      seen.add(k);
      out.push(s);
      if (out.length >= n) break;
    }
    return out;
  };
  return normalizeSkillPayload({
    name: existing.name || candidate.name,
    description:
      asString(candidate.description).length > asString(existing.description).length
        ? candidate.description
        : existing.description,
    prompt: asString(candidate.prompt).length > asString(existing.prompt).length ? candidate.prompt : existing.prompt,
    triggers: mergeSet(existing.triggers, candidate.triggers, 8),
    tags: mergeSet(existing.tags, candidate.tags, 10),
  }, existing);
}

function writeSkill({ skillBankDir, userId, dirName, skill, existing }) {
  const userRoot = path.join(skillBankDir, "Users", slug(userId || "default", "default"));
  const targetDir = path.join(userRoot, dirName);
  ensureDir(targetDir);
  const md = renderSkillMd(
    skill,
    existing ? existing.parsedId : "",
    existing ? bumpPatch(existing.version) : "0.1.0",
  );
  const mdPath = path.join(targetDir, "SKILL.md");
  fs.writeFileSync(mdPath, md, "utf8");
  return { dirPath: targetDir, mdPath };
}

function mirrorSkillToOpenClaw({ openclawSkillsDir, skillDirPath }) {
  const name = path.basename(skillDirPath);
  const dst = path.join(openclawSkillsDir, name);
  ensureDir(openclawSkillsDir);
  if (fs.existsSync(dst)) {
    fs.rmSync(dst, { recursive: true, force: true });
  }
  fs.cpSync(skillDirPath, dst, { recursive: true, force: true });
  return dst;
}

function detectModelHint(event, ctx) {
  const candidates = [
    event?.model,
    event?.modelId,
    event?.model_id,
    event?.providerModel,
    event?.result?.model,
    ctx?.model,
    ctx?.modelId,
    ctx?.model_id,
    ctx?.providerModel,
    ctx?.resolvedModel,
    ctx?.resolved_model,
  ];
  for (const c of candidates) {
    const s = trimmed(c);
    if (s) return s;
  }
  return "";
}

function isInternalEvent(event, ctx) {
  return Boolean(
    asBool(event?.autoskill_internal, false) ||
      asBool(event?.metadata?.autoskill_internal, false) ||
      asBool(ctx?.autoskill_internal, false) ||
      asBool(ctx?.metadata?.autoskill_internal, false),
  );
}

function isMirrorInstallEnabled(cfg) {
  const mode = trimmed(cfg?.skillInstallMode).toLowerCase();
  if (!mode) return true;
  return mode === "openclaw_mirror";
}

function isDuplicateCandidate(existing, candidate) {
  if (!existing || !candidate) return false;
  const existingPrompt = normalizeComparableText(existing.prompt || existing.instructions);
  const candidatePrompt = normalizeComparableText(candidate.prompt || candidate.instructions);
  if (existingPrompt && candidatePrompt && existingPrompt === candidatePrompt) {
    return true;
  }
  const existingName = normalizeComparableText(existing.name);
  const candidateName = normalizeComparableText(candidate.name);
  if (!existingName || !candidateName || existingName !== candidateName) {
    return false;
  }
  if (!existingPrompt || !candidatePrompt) return false;
  const minLen = Math.min(existingPrompt.length, candidatePrompt.length);
  if (minLen < 40) return false;
  return existingPrompt.includes(candidatePrompt) || candidatePrompt.includes(existingPrompt);
}

export function createEmbeddedProcessor(cfg, api, log, deps = {}) {
  const state = {
    activeSessionByUser: new Map(),
    liveSessionByKey: new Map(),
    internalDepth: 0,
  };
  const invokeModel =
    typeof deps.invokeModel === "function" ? deps.invokeModel : createDefaultModelInvoker(cfg, api, log, deps);
  const promptPack = loadPromptPack(cfg, log);
  const renderSharedPrompt = (key, fallback, vars = {}) => sharedPrompt(promptPack, key, fallback, vars);

  function sessionFilePath(userId, sessionId) {
    const root = path.resolve(cfg.embedded.sessionArchiveDir);
    return path.join(root, slug(userId || "default", "default"), `${slug(sessionId, "session")}.jsonl`);
  }

  function sessionSnapshotPath(userId, sessionId) {
    const root = path.resolve(cfg.embedded.sessionArchiveDir);
    return path.join(root, slug(userId || "default", "default"), `${slug(sessionId, "session")}.latest.json`);
  }

  function sessionKey(userId, sessionId) {
    return `${userId}::${sessionId}`;
  }

  function appendSession(payload) {
    const uid = slug(payload.user || "default", "default");
    const sid = trimmed(payload.session_id);
    if (!sid) {
      return { ended: [], reason: "missing_session_id", path: "", snapshot_path: "" };
    }
    const ended = [];
    const now = nowMs();
    const turnType = trimmed(payload.turn_type).toLowerCase();
    const success = Boolean(payload.success);
    const incomingMessages = sanitizeMessages(payload.messages);
    const prev = state.activeSessionByUser.get(uid);
    if (prev && prev !== sid) {
      const prevPath = sessionFilePath(uid, prev);
      const prevSnapshotPath = sessionSnapshotPath(uid, prev);
      const closedPrev = finalizeSessionFile(prevPath, "session_id_changed");
      const closedPrevSnapshot = finalizeSnapshotFile(prevSnapshotPath, "session_id_changed");
      state.liveSessionByKey.delete(sessionKey(uid, prev));
      if (closedPrev) {
        ended.push({
          user: uid,
          session_id: prev,
          path: closedPrev,
          snapshot_path: closedPrevSnapshot,
          reason: "session_id_changed",
        });
      }
    }
    const currentPath = sessionFilePath(uid, sid);
    const currentSnapshotPath = sessionSnapshotPath(uid, sid);
    appendJsonl(currentPath, {
      event_time: now,
      user_id: uid,
      session_id: sid,
      turn_type: turnType,
      session_done: Boolean(payload.session_done),
      success,
      messages: incomingMessages,
    });

    const key = sessionKey(uid, sid);
    const live =
      state.liveSessionByKey.get(key) ||
      {
        user_id: uid,
        session_id: sid,
        updated_at: 0,
        turn_count: 0,
        has_main: false,
        has_main_success: false,
        session_done: false,
        last_turn_type: "",
        messages: [],
      };
    live.updated_at = now;
    live.turn_count = Number(live.turn_count || 0) + 1;
    live.last_turn_type = turnType;
    live.session_done = Boolean(payload.session_done);
    if (turnType === "main") {
      live.has_main = true;
      if (success) live.has_main_success = true;
    }
    live.messages = mergeMessagesWithOverlap(live.messages, incomingMessages);
    state.liveSessionByKey.set(key, live);
    writeJson(currentSnapshotPath, live);

    state.activeSessionByUser.set(uid, sid);
    if (Boolean(payload.session_done)) {
      const closedCurrent = finalizeSessionFile(currentPath, "session_done");
      const closedSnapshot = finalizeSnapshotFile(currentSnapshotPath, "session_done");
      if (closedCurrent) {
        ended.push({
          user: uid,
          session_id: sid,
          path: closedCurrent,
          snapshot_path: closedSnapshot,
          reason: "session_done",
        });
      }
      state.activeSessionByUser.delete(uid);
      state.liveSessionByKey.delete(key);
    }
    return { ended, reason: "", path: currentPath, snapshot_path: currentSnapshotPath };
  }

  function loadClosedSession(item) {
    const records = readJsonl(item.path);
    let hasMain = false;
    let hasMainSuccess = false;
    let messages = [];
    for (const rec of records) {
      const turnType = trimmed(rec.turn_type).toLowerCase();
      const success = Boolean(rec.success);
      if (turnType === "main") {
        hasMain = true;
        if (success) hasMainSuccess = true;
      }
      messages = mergeMessagesWithOverlap(messages, sanitizeMessages(rec.messages));
    }
    return {
      ...item,
      records,
      messages,
      hasMain,
      hasMainSuccess,
    };
  }

  async function maintainSkill({ userId, candidate, modelHint }) {
    const skillBankDir = path.resolve(cfg.embedded.skillBankDir);
    const openclawSkillsDir = path.resolve(cfg.embedded.openclawSkillsDir);
    const mirrorEnabled = isMirrorInstallEnabled(cfg);
    const existingSkills = loadUserSkills(skillBankDir, userId);
    const duplicate = existingSkills.find((item) => isDuplicateCandidate(item, candidate));
    if (duplicate) {
      return {
        status: "skipped",
        reason: "duplicate_existing_skill",
        skill_id: duplicate.id,
      };
    }
    const hits = topBm25Hits(candidate, existingSkills, cfg.embedded.bm25TopK);
    const decision = await decideAction({
      invokeModel,
      candidate,
      hits,
      model: modelHint,
      metadata: { autoskill_internal: true, channel: "autoskill_embedded_maintain" },
      renderSharedPrompt,
    });
    if (decision.action === "discard") {
      return { status: "discarded", reason: "decision_discard" };
    }
    if (decision.action === "merge") {
      const target = existingSkills.find((x) => x.id === decision.target);
      if (!target) {
        return { status: "skipped", reason: "merge_target_missing" };
      }
      const merged = await mergeSkillWithModel({
        invokeModel,
        existing: target,
        candidate,
        model: modelHint,
        metadata: { autoskill_internal: true, channel: "autoskill_embedded_merge" },
        renderSharedPrompt,
      });
      const write = writeSkill({
        skillBankDir,
        userId,
        dirName: target.dirName,
        skill: merged,
        existing: target,
      });
      if (!mirrorEnabled) {
        return {
          status: "merged",
          skill_id: target.id,
          path: write.mdPath,
          mirror_skipped: true,
          mirror_reason: "install_mode_store_only",
        };
      }
      const mirrorPath = mirrorSkillToOpenClaw({
        openclawSkillsDir,
        skillDirPath: write.dirPath,
      });
      return { status: "merged", skill_id: target.id, path: write.mdPath, mirror_path: mirrorPath };
    }

    const baseName = slug(candidate.name, "skill");
    const taken = new Set(existingSkills.map((x) => x.dirName));
    let dirName = baseName;
    let idx = 2;
    while (taken.has(dirName)) {
      dirName = `${baseName}-${idx}`;
      idx += 1;
    }
    const write = writeSkill({
      skillBankDir,
      userId,
      dirName,
      skill: candidate,
      existing: null,
    });
    if (!mirrorEnabled) {
      return {
        status: "added",
        skill_id: dirName,
        path: write.mdPath,
        mirror_skipped: true,
        mirror_reason: "install_mode_store_only",
      };
    }
    const mirrorPath = mirrorSkillToOpenClaw({
      openclawSkillsDir,
      skillDirPath: write.dirPath,
    });
    return { status: "added", skill_id: dirName, path: write.mdPath, mirror_path: mirrorPath };
  }

  async function handle(payload, event, ctx) {
    if (!payload || typeof payload !== "object") {
      return { status: "skipped", reason: "empty_payload" };
    }
    if (isInternalEvent(event, ctx)) {
      return { status: "skipped", reason: "internal_extraction_event" };
    }
    if (state.internalDepth > 0) {
      return { status: "skipped", reason: "internal_extraction_busy" };
    }
    const staged = appendSession(payload);
    if (!staged.ended.length) {
      return {
        status: "skipped",
        reason: staged.reason || "session_not_finished",
        session_path: staged.path,
        session_snapshot_path: staged.snapshot_path,
      };
    }

    const modelHint = detectModelHint(event, ctx);
    const results = [];
    for (const ended of staged.ended) {
      const session = loadClosedSession(ended);
      if (!session.hasMain || !session.hasMainSuccess) {
        results.push({ session_id: session.session_id, status: "skipped", reason: "no_successful_main_turn" });
        continue;
      }
      if (!session.messages.length) {
        results.push({ session_id: session.session_id, status: "skipped", reason: "empty_session_messages" });
        continue;
      }
      state.internalDepth += 1;
      try {
        const candidate = await extractCandidate({
          invokeModel,
          sessionMessages: session.messages,
          model: modelHint,
          metadata: { autoskill_internal: true, channel: "autoskill_embedded_extract" },
          renderSharedPrompt,
        });
        if (!candidate) {
          results.push({ session_id: session.session_id, status: "skipped", reason: "no_candidate" });
          continue;
        }
        const maintain = await maintainSkill({
          userId: payload.user,
          candidate,
          modelHint,
        });
        results.push({ session_id: session.session_id, ...maintain });
      } catch (err) {
        results.push({ session_id: session.session_id, status: "failed", reason: String(err) });
      } finally {
        state.internalDepth = Math.max(0, state.internalDepth - 1);
      }
    }
    const changed = results.filter((x) => x.status === "added" || x.status === "merged");
    return {
      status: changed.length ? "scheduled" : "skipped",
      reason: changed.length ? "" : "session_not_extractable",
      jobs: results,
    };
  }

  return { handle };
}
