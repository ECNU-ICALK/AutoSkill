import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";

import plugin, {
  buildEndPayload,
  createSessionRetrievalCache,
  createAgentEndHandler,
  createBeforePromptBuildHandler,
  normalizeConfig,
} from "./index.js";

function makeLogger() {
  const entries = [];
  return {
    entries,
    info(message) {
      entries.push({ level: "info", message: String(message) });
    },
    warn(message) {
      entries.push({ level: "warn", message: String(message) });
    },
  };
}

function makeConfig(overrides = {}) {
  const skillRetrieval = {
    enabled: true,
    ...(overrides.skillRetrieval || {}),
  };
  return normalizeConfig({
    baseUrl: "http://127.0.0.1:9100/v1",
    extractOnAgentEnd: false,
    logPayload: false,
    ...overrides,
    skillRetrieval,
  });
}

async function withEnv(pairs, fn) {
  const prev = new Map();
  for (const [key, value] of Object.entries(pairs)) {
    prev.set(key, Object.prototype.hasOwnProperty.call(process.env, key) ? process.env[key] : undefined);
    if (value == null) delete process.env[key];
    else process.env[key] = String(value);
  }
  try {
    return await fn();
  } finally {
    for (const [key, value] of prev.entries()) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function sampleResult(overrides = {}) {
  return {
    selected_skills: [
      {
        id: "skill-1",
        name: "Release Checklist",
        description: "Apply when the user needs a concise release workflow.",
        triggers: ["the user asks about release flow"],
        instructions: "List checks\nCall out rollback criteria\nKeep the answer concise",
        tags: ["release", "ops"],
      },
    ],
    ...overrides,
  };
}

test("before_prompt_build returns no-op when skill retrieval is disabled", async () => {
  const logger = makeLogger();
  const cfg = makeConfig({
    skillRetrieval: {
      enabled: false,
    },
  });
  let called = false;
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      called = true;
      return sampleResult();
    },
  });

  const result = await handler(
    { messages: [{ role: "user", content: "How do I ship this?" }] },
    {},
  );

  assert.equal(result, undefined);
  assert.equal(called, false);
  assert(logger.entries.some((entry) => entry.message.includes("retrieval disabled")));
});

test("before_prompt_build skips external retrieval in embedded runtime default mode", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const logger = makeLogger();
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: true,
      });
      let called = false;
      const handler = createBeforePromptBuildHandler(cfg, logger, {
        async postJson() {
          called = true;
          return sampleResult();
        },
      });

      const result = await handler(
        { messages: [{ role: "user", content: "Need skill help." }] },
        {},
      );

      assert.equal(result, undefined);
      assert.equal(called, false);
      assert(
        logger.entries.some((entry) => entry.message.includes("retrieval disabled by embedded runtime mode")),
      );
    },
  );
});

test("before_prompt_build stages embedded live session snapshot even when retrieval is disabled", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const logger = makeLogger();
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: true,
      });
      let requestCalled = false;
      const liveCalls = [];
      const handler = createBeforePromptBuildHandler(cfg, logger, {
        embeddedProcessor: {
          async stageLive(payload) {
            liveCalls.push(payload);
            return { status: "staged" };
          },
        },
        async postJson() {
          requestCalled = true;
          return sampleResult();
        },
      });

      const result = await handler(
        {
          sessionId: "sess-live-stage",
          turnType: "main",
          messages: [{ role: "user", content: "Need skill help." }],
        },
        {},
      );

      assert.equal(result, undefined);
      assert.equal(requestCalled, false);
      assert.equal(liveCalls.length, 1);
      assert.equal(liveCalls[0].session_id, "sess-live-stage");
      assert.equal(liveCalls[0].session_done, false);
      assert(
        logger.entries.some((entry) => entry.message.includes("retrieval disabled by embedded runtime mode")),
      );
    },
  );
});

test("normalizeConfig disables retrieval by default when openclaw_mirror install mode is active", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "openclaw_mirror",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: false,
      });
      assert.equal(cfg.skillInstallMode, "openclaw_mirror");
      assert.equal(cfg.skillRetrieval.enabled, false);
      assert.equal(cfg.skillRetrieval.disableReason, "openclaw_mirror_install_mode");
    },
  );
});

test("normalizeConfig enables retrieval by default when store_only install mode is active", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: false,
      });
      assert.equal(cfg.skillInstallMode, "store_only");
      assert.equal(cfg.skillRetrieval.enabled, true);
      assert.equal(cfg.skillRetrieval.disableReason, "");
    },
  );
});

test("normalizeConfig re-enables retrieval for store_only when legacy mirror defaults are still present", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: false,
        recallEnabled: false,
        skillRetrieval: {
          enabled: false,
          topK: 3,
          maxChars: 1500,
          minScore: 0.4,
          injectionMode: "appendSystemContext",
        },
      });
      assert.equal(cfg.skillInstallMode, "store_only");
      assert.equal(cfg.skillRetrieval.enabled, true);
      assert.equal(cfg.skillRetrieval.disableReason, "");
    },
  );
});

test("normalizeConfig keeps retrieval disabled in store_only when explicitly disabled by env", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "0",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: false,
      });
      assert.equal(cfg.skillInstallMode, "store_only");
      assert.equal(cfg.skillRetrieval.enabled, false);
    },
  );
});

test("normalizeConfig disables retrieval by default in embedded runtime mode", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
      assert.equal(cfg.skillRetrieval.enabled, false);
      assert.equal(cfg.skillRetrieval.disableReason, "embedded_runtime_mode");
    },
  );
});

test("normalizeConfig allows explicit retrieval opt-in in embedded runtime mode", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "store_only",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "1",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
      assert.equal(cfg.skillRetrieval.enabled, true);
      assert.equal(cfg.skillRetrieval.disableReason, "");
    },
  );
});

test("normalizeConfig still allows explicit retrieval opt-in under openclaw_mirror", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE: "openclaw_mirror",
      AUTOSKILL_SKILL_RETRIEVAL_ENABLED: "",
    },
    async () => {
      const cfg = normalizeConfig({
        baseUrl: "http://127.0.0.1:9100/v1",
        extractOnAgentEnd: false,
        skillRetrieval: {
          enabled: true,
        },
      });
      assert.equal(cfg.skillInstallMode, "openclaw_mirror");
      assert.equal(cfg.skillRetrieval.enabled, true);
      assert.equal(cfg.skillRetrieval.disableReason, "");
    },
  );
});

test("normalizeConfig keeps legacy maxInjectedChars alias compatible with 1500-char defaults", () => {
  const cfg = normalizeConfig({
    baseUrl: "http://127.0.0.1:9100/v1",
    extractOnAgentEnd: false,
    maxInjectedChars: 1500,
  });

  assert.equal(cfg.maxInjectedChars, 1500);
  assert.equal(cfg.skillRetrieval.maxChars, 1500);
});

test("before_prompt_build returns no-op when retrieval returns no skills", async () => {
  const logger = makeLogger();
  const cfg = makeConfig();
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return { selected_skills: [] };
    },
  });

  const result = await handler(
    { messages: [{ role: "user", content: "Find me nothing." }] },
    {},
  );

  assert.equal(result, undefined);
  assert(logger.entries.some((entry) => entry.message.includes("retrieval no result")));
});

test("before_prompt_build appends concise skill hints when retrieval succeeds", async () => {
  const logger = makeLogger();
  const cfg = makeConfig();
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return sampleResult();
    },
  });

  const result = await handler(
    {
      systemPrompt: "Keep system prompt intact",
      messages: [{ role: "user", content: "Need a release checklist." }],
    },
    {},
  );

  assert.ok(result);
  assert.ok("appendSystemContext" in result);
  assert.equal("systemPrompt" in result, false);
  assert.match(result.appendSystemContext, /## AutoSkill Skill Hints/);
  assert.match(result.appendSystemContext, /Release Checklist/);
  assert.match(result.appendSystemContext, /Applicable when:/);
  assert.match(result.appendSystemContext, /Key hints:/);
  assert.match(result.appendSystemContext, /ignore it and continue with the normal prompt and memory context/i);
  assert(logger.entries.some((entry) => entry.message.includes("retrieval success skills=1")));
});

test("before_prompt_build does not mutate the original messages array", async () => {
  const logger = makeLogger();
  const cfg = makeConfig();
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return sampleResult();
    },
  });
  const messages = [
    { role: "system", content: "base system prompt" },
    { role: "user", content: "Help me release safely." },
  ];
  const before = cloneJson(messages);

  await handler({ messages }, {});

  assert.deepEqual(messages, before);
});

test("before_prompt_build swallows retrieval errors and keeps the main flow alive", async () => {
  const logger = makeLogger();
  const cfg = makeConfig();
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      throw new Error("sidecar unavailable");
    },
  });

  const result = await handler(
    { messages: [{ role: "user", content: "Release now." }] },
    {},
  );

  assert.equal(result, undefined);
  assert(
    logger.entries.some(
      (entry) => entry.level === "warn" && entry.message.includes("retrieval failed"),
    ),
  );
});

test("before_prompt_build truncates injected context to the configured maxChars", async () => {
  const logger = makeLogger();
  const cfg = makeConfig({
    skillRetrieval: {
      maxChars: 220,
    },
  });
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return sampleResult({
        selected_skills: [
          {
            id: "skill-1",
            name: "Long Skill",
            description:
              "Apply when the user needs a long summary repeated many times. ".repeat(12),
            instructions:
              "First long instruction sentence. ".repeat(12) +
              "\n" +
              "Second long instruction sentence. ".repeat(12),
          },
        ],
      });
    },
  });

  const result = await handler(
    { messages: [{ role: "user", content: "Need the long version." }] },
    {},
  );

  assert.ok(result?.appendSystemContext);
  assert(result.appendSystemContext.length <= 220);
  assert.match(result.appendSystemContext, /\.\.\.\[autoskill context truncated\]\.\.\./);
});

test("before_prompt_build does not modify memory-related context state", async () => {
  const logger = makeLogger();
  const cfg = makeConfig();
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return sampleResult();
    },
  });
  const ctx = {
    plugins: {
      slots: {
        memory: {
          enabled: true,
          provider: "workspace-memory",
        },
      },
    },
    memory: {
      workspaceFile: "MEMORY.md",
    },
  };
  const before = cloneJson(ctx);

  await handler(
    { messages: [{ role: "user", content: "Use memory and help me release." }] },
    ctx,
  );

  assert.deepEqual(ctx, before);
});

test("before_prompt_build is stable across repeated calls and does not inflate the injected block", async () => {
  const logger = makeLogger();
  const cfg = makeConfig();
  const handler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return sampleResult();
    },
  });
  const event = {
    messages: [{ role: "user", content: "Need a release checklist." }],
  };

  const first = await handler(event, {});
  const second = await handler(event, {});

  assert.deepEqual(second, first);
  assert.equal(
    first.appendSystemContext.match(/## AutoSkill Skill Hints/g)?.length ?? 0,
    1,
  );
});

test("plugin registers before_prompt_build without re-registering before_agent_start", () => {
  const hooks = [];
  plugin.register({
    pluginConfig: {
      skillRetrieval: { enabled: false },
      extractOnAgentEnd: false,
    },
    logger: makeLogger(),
    registerHook(name, handler, meta) {
      hooks.push({ name, handler, meta });
    },
  });

  const names = hooks.map((hook) => hook.name);
  assert.equal(names.includes("before_prompt_build"), true);
  assert.equal(names.includes("beforePromptBuild"), true);
  assert.equal(names.includes("agent_end"), true);
  assert.equal(names.includes("agentEnd"), true);
  assert.equal(hooks.some((hook) => hook.name === "before_agent_start"), false);
});

test("agent_end payload includes session and turn metadata when available", () => {
  const cfg = makeConfig();
  const payload = buildEndPayload(
    cfg,
    {
      sessionId: "sess-1",
      turnType: "main",
      sessionDone: true,
      channel: "cli",
      messages: [
        { role: "user", content: "Do the task." },
        { role: "assistant", content: "Done." },
      ],
    },
    {},
  );

  assert.equal(payload.session_id, "sess-1");
  assert.equal(payload.turn_type, "main");
  assert.equal(payload.session_done, true);
  assert.equal(payload.channel, "cli");
});

test("buildEndPayload infers main turn_type when runtime omits turnType fields", () => {
  const cfg = makeConfig();
  const payload = buildEndPayload(
    cfg,
    {
      sessionId: "sess-infer-main",
      messages: [
        { role: "user", content: "Do this task." },
        { role: "assistant", content: "Done." },
      ],
    },
    {},
  );

  assert.equal(payload.turn_type, "main");
});

test("buildEndPayload infers side turn_type when only tool/environment messages exist", () => {
  const cfg = makeConfig();
  const payload = buildEndPayload(
    cfg,
    {
      sessionId: "sess-infer-side",
      messages: [
        { role: "environment", content: "tool output only" },
      ],
    },
    {},
  );

  assert.equal(payload.turn_type, "side");
});

test("buildEndPayload preserves assistant tool-call messages and maps environment to tool", () => {
  const cfg = makeConfig();
  const payload = buildEndPayload(
    cfg,
    {
      sessionId: "sess-tools",
      turnType: "main",
      sessionDone: false,
      messages: [
        { role: "user", content: "Run checks." },
        {
          role: "assistant",
          content: "",
          tool_calls: [{ id: "tc_1", type: "function", function: { name: "run_checks", arguments: "{}" } }],
        },
        { role: "environment", content: "workspace ready" },
      ],
    },
    {},
  );

  assert.equal(payload.messages.length, 3);
  assert.equal(payload.messages[1].role, "assistant");
  assert.match(payload.messages[1].content, /tool_calls/);
  assert.equal(payload.messages[2].role, "tool");
  assert.equal(payload.messages[2].content, "workspace ready");
});

test("normalizeConfig can switch to embedded runtime mode", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_SKILLBANK_DIR: "/tmp/autoskill-skillbank",
    },
    async () => {
      const cfg = normalizeConfig({
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
      assert.equal(cfg.embedded.skillBankDir, "/tmp/autoskill-skillbank");
      assert.equal(cfg.embedded.bm25TopK, 8);
      assert.deepEqual(cfg.embedded.modelInvocation.modes, [
        "openclaw-runtime",
        "openclaw-runtime-subagent",
        "openclaw-config-resolve",
        "manual",
      ]);
    },
  );
});

test("normalizeConfig supports embedded model invocation env overrides", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_MODES: "openclaw-runtime-subagent,openclaw-config-resolve,manual",
      AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_TIMEOUT_MS: "35000",
      AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_RETRIES: "2",
      AUTOSKILL_OPENCLAW_EMBEDDED_OPENCLAW_HOME: "/tmp/openclaw-home",
      AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_BASE_URL: "http://127.0.0.1:8999/v1/",
      AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_API_KEY: "k-test",
      AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_MODEL: "m-test",
    },
    async () => {
      const cfg = normalizeConfig({
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
      assert.deepEqual(cfg.embedded.modelInvocation.modes, [
        "openclaw-runtime-subagent",
        "openclaw-config-resolve",
        "manual",
      ]);
      assert.equal(cfg.embedded.modelInvocation.timeoutMs, 35000);
      assert.equal(cfg.embedded.modelInvocation.retries, 2);
      assert.equal(cfg.embedded.modelInvocation.openclawHome, "/tmp/openclaw-home");
      assert.equal(cfg.embedded.modelInvocation.manualBaseUrl, "http://127.0.0.1:8999/v1");
      assert.equal(cfg.embedded.modelInvocation.manualApiKey, "k-test");
      assert.equal(cfg.embedded.modelInvocation.manualModel, "m-test");
    },
  );
});

test("normalizeConfig supports embedded prompt pack path from plugin config", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH: "",
    },
    async () => {
      const cfg = normalizeConfig({
        extractOnAgentEnd: true,
        embedded: {
          promptPackPath: "./tmp/custom-openclaw-pack.txt",
        },
      });
      assert.equal(cfg.runtimeMode, "embedded");
      assert.equal(
        cfg.embedded.promptPackPath,
        path.resolve("./tmp/custom-openclaw-pack.txt"),
      );
    },
  );
});

test("normalizeConfig supports embedded prompt pack path from env", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "embedded",
      AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH: "/tmp/openclaw-shared-pack.txt",
    },
    async () => {
      const cfg = normalizeConfig({
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
      assert.equal(cfg.embedded.promptPackPath, "/tmp/openclaw-shared-pack.txt");
    },
  );
});

test("normalizeConfig enables embedded runtime via no-sidecar env alias", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "",
      AUTOSKILL_OPENCLAW_NO_SIDECAR: "1",
    },
    async () => {
      const cfg = normalizeConfig({
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
    },
  );
});

test("normalizeConfig keeps explicit sidecar runtime even when no-sidecar env alias is set", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "",
      AUTOSKILL_OPENCLAW_NO_SIDECAR: "1",
    },
    async () => {
      const cfg = normalizeConfig({
        runtimeMode: "sidecar",
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "sidecar");
    },
  );
});

test("normalizeConfig treats empty runtimeMode config as unset and still honors no-sidecar alias", async () => {
  await withEnv(
    {
      AUTOSKILL_OPENCLAW_RUNTIME_MODE: "",
      AUTOSKILL_OPENCLAW_NO_SIDECAR: "1",
    },
    async () => {
      const cfg = normalizeConfig({
        runtimeMode: "",
        extractOnAgentEnd: true,
      });
      assert.equal(cfg.runtimeMode, "embedded");
    },
  );
});

test("agent_end routes to sidecar request in sidecar mode", async () => {
  const logger = makeLogger();
  const cfg = normalizeConfig({
    runtimeMode: "sidecar",
    extractOnAgentEnd: true,
    successOnly: true,
    skillRetrieval: { enabled: false },
  });
  const sent = [];
  const handler = createAgentEndHandler(cfg, logger, {
    async postJson(_cfg, path, payload) {
      sent.push({ path, payload });
      return { ok: true };
    },
    embeddedProcessor: {
      async handle() {
        throw new Error("embedded should not be called in sidecar mode");
      },
    },
  });
  await handler(
    {
      sessionId: "sess-sidecar",
      turnType: "main",
      messages: [{ role: "user", content: "do it" }],
      success: true,
    },
    {},
  );

  assert.equal(sent.length, 1);
  assert.equal(sent[0].path, "/autoskill/openclaw/hooks/agent_end");
  assert.equal(sent[0].payload.session_id, "sess-sidecar");
});

test("agent_end forwards cached retrieval snapshot and explicit used_skill_ids", async () => {
  const logger = makeLogger();
  const cfg = normalizeConfig({
    runtimeMode: "sidecar",
    extractOnAgentEnd: true,
    successOnly: true,
    skillRetrieval: { enabled: true, topK: 3, minScore: 0.1, maxChars: 1200 },
  });
  const sent = [];
  const retrievalCache = new Map();
  const beforeHandler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return {
        query: "release checklist",
        selected_for_context_ids: ["skill-1"],
        selected_for_use_ids: ["skill-1"],
        hits: [
          {
            id: "skill-1",
            name: "Release Checklist",
            description: "Checklist for release",
            score: 0.91,
          },
        ],
      };
    },
    onRetrieval(sessionId, snapshot) {
      retrievalCache.set(sessionId, snapshot);
    },
  });
  const endHandler = createAgentEndHandler(cfg, logger, {
    async postJson(_cfg, path, payload) {
      sent.push({ path, payload });
      return { ok: true };
    },
    consumeRetrieval(sessionId) {
      const snapshot = retrievalCache.get(sessionId) || null;
      retrievalCache.delete(sessionId);
      return snapshot;
    },
  });

  await beforeHandler(
    {
      sessionId: "sess-usage-1",
      messages: [{ role: "user", content: "Need release checklist." }],
    },
    {},
  );
  await endHandler(
    {
      sessionId: "sess-usage-1",
      used_skill_ids: ["skill-1"],
      messages: [
        { role: "user", content: "Need release checklist." },
        { role: "assistant", content: "Using the checklist now." },
      ],
      success: true,
    },
    {},
  );

  assert.equal(sent.length, 1);
  assert.equal(sent[0].path, "/autoskill/openclaw/hooks/agent_end");
  assert.deepEqual(sent[0].payload.used_skill_ids, ["skill-1"]);
  assert.equal(sent[0].payload.retrieval.selected_for_context_ids[0], "skill-1");
  assert.equal(sent[0].payload.retrieval.hits[0].id, "skill-1");
});

test("agent_end forwards inferred_used_skill_ids when explicit signal is absent", async () => {
  const logger = makeLogger();
  const cfg = normalizeConfig({
    runtimeMode: "sidecar",
    extractOnAgentEnd: true,
    successOnly: true,
    skillRetrieval: { enabled: true, topK: 3, minScore: 0.1, maxChars: 1200 },
  });
  const sent = [];
  const retrievalCache = new Map();
  const beforeHandler = createBeforePromptBuildHandler(cfg, logger, {
    async postJson() {
      return {
        query: "deployment rollback",
        selected_for_context_ids: ["skill-rb"],
        selected_for_use_ids: ["skill-rb"],
        hits: [
          {
            id: "skill-rb",
            name: "Rollback Procedure",
            description: "Rollback deployment safely",
            score: 0.88,
          },
        ],
      };
    },
    onRetrieval(sessionId, snapshot) {
      retrievalCache.set(sessionId, snapshot);
    },
  });
  const endHandler = createAgentEndHandler(cfg, logger, {
    async postJson(_cfg, path, payload) {
      sent.push({ path, payload });
      return { ok: true };
    },
    consumeRetrieval(sessionId) {
      const snapshot = retrievalCache.get(sessionId) || null;
      retrievalCache.delete(sessionId);
      return snapshot;
    },
  });

  await beforeHandler(
    {
      sessionId: "sess-usage-infer",
      messages: [{ role: "user", content: "Need rollback procedure." }],
    },
    {},
  );
  await endHandler(
    {
      sessionId: "sess-usage-infer",
      messages: [
        { role: "user", content: "Need rollback procedure." },
        { role: "assistant", content: "I will apply rollback procedure." },
      ],
      success: true,
    },
    {},
  );

  assert.equal(sent.length, 1);
  assert.equal(sent[0].path, "/autoskill/openclaw/hooks/agent_end");
  assert.ok(Array.isArray(sent[0].payload.inferred_used_skill_ids));
  assert.deepEqual(sent[0].payload.inferred_used_skill_ids, ["skill-rb"]);
  assert.equal(sent[0].payload.used_skill_ids, undefined);
});

test("agent_end routes to embedded processor in embedded mode", async () => {
  const logger = makeLogger();
  const cfg = normalizeConfig({
    runtimeMode: "embedded",
    extractOnAgentEnd: true,
    successOnly: true,
    skillRetrieval: { enabled: false },
  });
  const embeddedCalls = [];
  const handler = createAgentEndHandler(cfg, logger, {
    async postJson() {
      throw new Error("sidecar request should not be sent in embedded mode");
    },
    embeddedProcessor: {
      async handle(payload) {
        embeddedCalls.push(payload);
        return { status: "scheduled" };
      },
    },
  });
  await handler(
    {
      sessionId: "sess-embedded",
      turnType: "main",
      messages: [{ role: "user", content: "build skill" }],
      success: true,
    },
    {},
  );

  assert.equal(embeddedCalls.length, 1);
  assert.equal(embeddedCalls[0].session_id, "sess-embedded");
  assert.equal(embeddedCalls[0].turn_type, "main");
});

test("session retrieval cache isolates same session_id across different users", () => {
  const cache = createSessionRetrievalCache();
  const snapshotA = { query: "q-a", hits: [{ id: "skill-a", score: 0.8 }] };
  const snapshotB = { query: "q-b", hits: [{ id: "skill-b", score: 0.9 }] };

  cache.remember("sess-1", snapshotA, "user-a");
  cache.remember("sess-1", snapshotB, "user-b");

  assert.deepEqual(cache.consume("sess-1", "user-a"), snapshotA);
  assert.deepEqual(cache.consume("sess-1", "user-b"), snapshotB);
  assert.equal(cache.consume("sess-1", "user-a"), null);
});

test("session retrieval cache keeps backward compatibility when user id is missing", () => {
  const cache = createSessionRetrievalCache();
  const snapshot = { query: "q", hits: [{ id: "skill-a" }] };
  cache.remember("sess-legacy", snapshot);
  assert.deepEqual(cache.consume("sess-legacy"), snapshot);
});
