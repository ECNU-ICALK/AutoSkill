import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { createEmbeddedProcessor } from "./embedded_runtime.js";

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

function makeSandbox() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "autoskill-embedded-"));
  const sessionArchiveDir = path.join(root, "sessions");
  const skillBankDir = path.join(root, "SkillBank");
  const openclawSkillsDir = path.join(root, "openclaw-skills");
  fs.mkdirSync(sessionArchiveDir, { recursive: true });
  fs.mkdirSync(skillBankDir, { recursive: true });
  fs.mkdirSync(openclawSkillsDir, { recursive: true });
  return { root, sessionArchiveDir, skillBankDir, openclawSkillsDir };
}

function makeConfig(paths, overrides = {}) {
  const embeddedOverride = overrides.embedded || {};
  const base = { ...overrides };
  delete base.embedded;
  return {
    skillInstallMode: "openclaw_mirror",
    ...base,
    embedded: {
      sessionArchiveDir: paths.sessionArchiveDir,
      skillBankDir: paths.skillBankDir,
      openclawSkillsDir: paths.openclawSkillsDir,
      bm25TopK: 8,
      ...embeddedOverride,
    },
  };
}

function listSkillDirs(skillBankDir, userId = "user1") {
  const userRoot = path.join(skillBankDir, "Users", userId);
  if (!fs.existsSync(userRoot)) return [];
  return fs.readdirSync(userRoot, { withFileTypes: true }).filter((entry) => entry.isDirectory());
}

function writeExistingSkill({
  skillBankDir,
  userId = "user1",
  dirName = "existing-skill",
  name = "Existing Skill",
  description = "Existing reusable skill.",
  prompt = "Do existing workflow.\nCheck constraints.",
  triggers = ["when requested"],
  tags = [],
  files = {},
}) {
  const dir = path.join(skillBankDir, "Users", userId, dirName);
  fs.mkdirSync(dir, { recursive: true });
  const resourcePaths = Object.keys(files || {}).filter((item) => item && item !== "SKILL.md").sort();
  const md = [
    "---",
    `id: "skill-${dirName}"`,
    `name: "${name}"`,
    `description: "${description}"`,
    'version: "0.1.0"',
    "---",
    "",
    `# ${name}`,
    "",
    description,
    "",
    "## Prompt",
    "",
    prompt,
    "",
    ...(resourcePaths.length
      ? [
          "## Files",
          "",
          ...resourcePaths.map((item) => `- \`${item}\``),
          "",
        ]
      : []),
    "## Triggers",
    "",
    ...triggers.map((item) => `- ${item}`),
    "",
    ...(tags.length
      ? [
          "## Tags",
          "",
          ...tags.map((item) => `- ${item}`),
          "",
        ]
      : []),
    "",
  ].join("\n");
  fs.writeFileSync(path.join(dir, "SKILL.md"), md, "utf8");
  for (const [relPath, content] of Object.entries(files || {})) {
    if (!relPath || relPath === "SKILL.md") continue;
    const absPath = path.join(dir, relPath);
    fs.mkdirSync(path.dirname(absPath), { recursive: true });
    fs.writeFileSync(absPath, String(content || ""), "utf8");
  }
  return dir;
}

function makeInvokeModelForAdd() {
  return async ({ metadata }) => {
    if (metadata?.channel === "autoskill_embedded_extract") {
      return JSON.stringify({
        skills: [
          {
            name: "Release Checklist",
            description: "Reusable release checklist for deployment workflows.",
            prompt: "Validate readiness.\nRun deployment checks.\nDocument rollback steps.",
            triggers: ["release workflow", "deployment checks"],
            tags: ["release", "ops"],
          },
        ],
      });
    }
    if (metadata?.channel === "autoskill_embedded_maintain") {
      return JSON.stringify({ action: "add" });
    }
    return JSON.stringify({});
  };
}

function makeHttpModelResponder(calls = []) {
  return async (url, opts) => {
    const body = JSON.parse(String(opts?.body || "{}"));
    calls.push({
      url: String(url),
      model: body?.model || "",
      channel: body?.metadata?.channel || "",
    });
    if (body?.metadata?.channel === "autoskill_embedded_extract") {
      return {
        ok: true,
        status: 200,
        text: async () =>
          JSON.stringify({
            choices: [
              {
                message: {
                  content: JSON.stringify({
                    skills: [
                      {
                        name: "Runtime HTTP Skill",
                        description: "Extracted through OpenAI-compatible HTTP fallback.",
                        prompt: "Do A.\nDo B.",
                        triggers: ["agent trajectory"],
                        tags: ["embedded"],
                      },
                    ],
                  }),
                },
              },
            ],
          }),
      };
    }
    if (body?.metadata?.channel === "autoskill_embedded_maintain") {
      return {
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ choices: [{ message: { content: JSON.stringify({ action: "add" }) } }] }),
      };
    }
    return {
      ok: true,
      status: 200,
      text: async () => JSON.stringify({ choices: [{ message: { content: "{}" } }] }),
    };
  };
}

function makeInvokeModelWithMultilineMetadata() {
  return async ({ metadata }) => {
    if (metadata?.channel === "autoskill_embedded_extract") {
      return JSON.stringify({
        skills: [
          {
            name: "Release\nChecklist \"Pro\"",
            description: "Reusable release checklist\nfor deployment workflows.",
            prompt: "# Goal\nShip safely.\n",
            triggers: ["release workflow", "deployment\nchecks"],
            tags: ["release", "ops\ncore"],
          },
        ],
      });
    }
    if (metadata?.channel === "autoskill_embedded_maintain") {
      return JSON.stringify({ action: "add" });
    }
    return JSON.stringify({});
  };
}

function makeInvokeModelWithFiles() {
  return async ({ metadata }) => {
    if (metadata?.channel === "autoskill_embedded_extract") {
      return JSON.stringify({
        skills: [
          {
            name: "Release Checklist",
            description: "Reusable release checklist for deployment workflows.",
            prompt: "Validate readiness.\nRead reference: references/release-checklist.md.\nExecute script: scripts/release_gate.sh.",
            triggers: ["release workflow", "deployment checks"],
            tags: ["release", "ops"],
            files: {
              "scripts/release_gate.sh": "#!/usr/bin/env bash\necho release-gate\n",
              "references/release-checklist.md": "# Release checklist\n- Verify rollback.\n",
              "assets/release-template.txt": "rollback_owner=<OWNER>\n",
            },
          },
        ],
      });
    }
    if (metadata?.channel === "autoskill_embedded_maintain") {
      return JSON.stringify({ action: "add" });
    }
    return JSON.stringify({});
  };
}

test("embedded runtime persists live session snapshot before session end", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  let invokeCount = 0;
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    async invokeModel() {
      invokeCount += 1;
      return JSON.stringify({});
    },
  });

  const first = await processor.handle(
    {
      user: "user1",
      session_id: "sess-live",
      turn_type: "main",
      session_done: false,
      success: true,
      messages: [
        { role: "user", content: "Need reusable release plan." },
        { role: "assistant", content: "Use checklist and rollback gate." },
      ],
    },
    {},
    {},
  );

  assert.equal(first.status, "skipped");
  assert.equal(first.reason, "session_not_finished");
  assert.equal(invokeCount, 0);
  assert.ok(first.session_path);
  assert.ok(first.session_snapshot_path);
  assert.equal(fs.existsSync(String(first.session_path)), true);
  assert.equal(fs.existsSync(String(first.session_snapshot_path)), true);

  const snap1 = JSON.parse(fs.readFileSync(String(first.session_snapshot_path), "utf8"));
  assert.equal(snap1.session_id, "sess-live");
  assert.equal(snap1.turn_count, 1);
  assert.equal(snap1.has_main, true);
  assert.equal(snap1.has_main_success, true);
  assert.equal(snap1.session_done, false);
  assert.equal(Array.isArray(snap1.messages), true);
  assert.equal(snap1.messages.length, 2);

  const second = await processor.handle(
    {
      user: "user1",
      session_id: "sess-live",
      turn_type: "side",
      session_done: false,
      success: true,
      messages: [
        { role: "assistant", content: "Use checklist and rollback gate." },
        { role: "tool", content: "workspace: clean" },
      ],
    },
    {},
    {},
  );

  assert.equal(second.status, "skipped");
  assert.equal(second.reason, "session_not_finished");
  assert.equal(invokeCount, 0);
  const snap2 = JSON.parse(fs.readFileSync(String(second.session_snapshot_path), "utf8"));
  assert.equal(snap2.turn_count, 2);
  assert.equal(snap2.session_done, false);
  assert(snap2.messages.some((m) => m.role === "tool" && /workspace: clean/.test(m.content)));
});

test("embedded runtime reads shared prompt pack templates for extraction and maintenance", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const promptPackPath = path.join(paths.root, "openclaw_prompt_pack.txt");
  fs.writeFileSync(
    promptPackPath,
    [
      "@@version test-pack",
      "",
      "@@block shared.marker",
      "SHARED-MARKER-LINE",
      "@@end",
      "",
      "@@template embedded.extract.system",
      "EXTRACT-CUSTOM {{block.shared.marker}} max={{var.max_candidates}}",
      "@@end",
      "",
      "@@template embedded.maintain.decide.system",
      "DECIDE-CUSTOM {{block.shared.marker}}",
      "@@end",
      "",
      "@@template embedded.maintain.merge.system",
      "MERGE-CUSTOM {{block.shared.marker}}",
      "@@end",
      "",
    ].join("\n"),
    "utf8",
  );

  const seenCalls = [];
  const processor = createEmbeddedProcessor(
    makeConfig(paths, { embedded: { promptPackPath } }),
    {},
    logger,
    {
      async invokeModel({ system, metadata }) {
        seenCalls.push({ channel: metadata?.channel || "", system: String(system || "") });
        if (metadata?.channel === "autoskill_embedded_extract") {
          return JSON.stringify({
            skills: [
              {
                name: "Prompt Pack Skill",
                description: "Skill extracted with custom prompt pack.",
                prompt: "# Goal\nDo it.\n",
                triggers: ["prompt pack extract"],
                tags: ["prompt-pack"],
              },
            ],
          });
        }
        if (metadata?.channel === "autoskill_embedded_maintain") {
          return JSON.stringify({ action: "add" });
        }
        return JSON.stringify({});
      },
    },
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-prompt-pack",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need reusable process." },
        { role: "assistant", content: "Sure." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "scheduled");
  const extract = seenCalls.find((x) => x.channel === "autoskill_embedded_extract");
  const decide = seenCalls.find((x) => x.channel === "autoskill_embedded_maintain");
  assert.ok(extract);
  assert.ok(decide);
  assert.match(extract.system, /EXTRACT-CUSTOM/);
  assert.match(extract.system, /SHARED-MARKER-LINE/);
  assert.match(extract.system, /max=1/);
  assert.match(decide.system, /DECIDE-CUSTOM/);
  assert.match(decide.system, /SHARED-MARKER-LINE/);
});

test("embedded runtime extracts only after session is closed and mirrors changed skills", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    invokeModel: makeInvokeModelForAdd(),
  });

  const pending = await processor.handle(
    {
      user: "user1",
      session_id: "sess-1",
      turn_type: "main",
      session_done: false,
      success: true,
      messages: [
        { role: "user", content: "How to run a release?" },
        { role: "assistant", content: "Follow a release checklist." },
      ],
    },
    {},
    {},
  );
  assert.equal(pending.status, "skipped");
  assert.equal(pending.reason, "session_not_finished");

  const done = await processor.handle(
    {
      user: "user1",
      session_id: "sess-1",
      turn_type: "side",
      session_done: true,
      success: true,
      messages: [{ role: "user", content: "Thanks." }],
    },
    {},
    {},
  );
  assert.equal(done.status, "scheduled");
  assert(done.jobs.some((job) => job.status === "added"));

  const userSkillDirs = listSkillDirs(paths.skillBankDir, "user1");
  assert.equal(userSkillDirs.length, 1);
  const skillDirName = userSkillDirs[0].name;
  assert.ok(fs.existsSync(path.join(paths.skillBankDir, "Users", "user1", skillDirName, "SKILL.md")));
  assert.ok(fs.existsSync(path.join(paths.openclawSkillsDir, skillDirName, "SKILL.md")));
});

test("embedded runtime persists bundled resource files into SkillBank and mirrored OpenClaw skills", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    invokeModel: makeInvokeModelWithFiles(),
  });

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-files",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need a reusable release workflow with helper files." },
        { role: "assistant", content: "Will capture the checklist and script." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "scheduled");
  const added = result.jobs.find((job) => job.status === "added");
  assert.ok(added?.path);
  const skillDir = path.dirname(String(added.path));
  const mirroredDir = path.join(paths.openclawSkillsDir, path.basename(skillDir));
  const md = fs.readFileSync(String(added.path), "utf8");
  assert.match(md, /## Files/);
  assert.match(md, /`scripts\/release_gate\.sh`/);
  assert.equal(fs.existsSync(path.join(skillDir, "scripts", "release_gate.sh")), true);
  assert.equal(fs.existsSync(path.join(skillDir, "references", "release-checklist.md")), true);
  assert.equal(fs.existsSync(path.join(skillDir, "assets", "release-template.txt")), true);
  assert.equal(fs.existsSync(path.join(mirroredDir, "scripts", "release_gate.sh")), true);
  assert.equal(fs.existsSync(path.join(mirroredDir, "references", "release-checklist.md")), true);
  assert.equal(fs.existsSync(path.join(mirroredDir, "assets", "release-template.txt")), true);
});

test("embedded runtime sends explicit user feedback and session evidence into extraction input", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const seen = [];
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    async invokeModel({ metadata, user }) {
      if (metadata?.channel === "autoskill_embedded_extract") {
        seen.push(JSON.parse(String(user || "{}")));
        return JSON.stringify({
          skills: [
            {
              name: "Feedback Aware Skill",
              description: "Skill extracted with end-of-session feedback.",
              prompt: "Use the validated workflow.",
              triggers: ["feedback aware"],
              tags: ["feedback"],
            },
          ],
        });
      }
      if (metadata?.channel === "autoskill_embedded_maintain") {
        return JSON.stringify({ action: "add" });
      }
      return JSON.stringify({});
    },
  });

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-feedback",
      turn_type: "main",
      session_done: true,
      success: true,
      user_feedback: "Keep the rollback verification and reuse it next time.",
      messages: [
        { role: "user", content: "Need a release workflow." },
        { role: "assistant", content: "I will prepare one." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "scheduled");
  assert.equal(seen.length, 1);
  const payload = seen[0];
  assert.equal(payload.session_evidence.has_main_turn, true);
  assert.equal(payload.session_evidence.has_successful_main_turn, true);
  assert.equal(payload.session_evidence.turn_count, 1);
  assert.equal(payload.session_evidence.turns[0].turn_type, "main");
  assert(payload.session_messages.some((item) => item.role === "user" && /rollback verification/.test(item.content)));
});

test("embedded runtime auto-closes long-lived session after max turn threshold", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        sessionMaxTurns: 2,
      },
    }),
    {},
    logger,
    {
      invokeModel: makeInvokeModelForAdd(),
    },
  );

  const first = await processor.handle(
    {
      user: "user1",
      session_id: "sess-turn-limit",
      turn_type: "main",
      session_done: false,
      success: true,
      messages: [
        { role: "user", content: "Need a reusable workflow." },
        { role: "assistant", content: "I will outline it." },
      ],
    },
    {},
    {},
  );
  assert.equal(first.status, "skipped");
  assert.equal(first.reason, "session_not_finished");

  const second = await processor.handle(
    {
      user: "user1",
      session_id: "sess-turn-limit",
      turn_type: "side",
      session_done: false,
      success: true,
      messages: [
        { role: "assistant", content: "Running reusable checks." },
        { role: "tool", content: "workspace: ready" },
      ],
    },
    {},
    {},
  );
  assert.equal(second.status, "scheduled");
  const added = second.jobs.find((job) => job.status === "added");
  assert.ok(added);
  assert.equal(listSkillDirs(paths.skillBankDir, "user1").length, 1);
});

test("embedded runtime requires at least one successful main turn", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  let invokeCount = 0;
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    async invokeModel() {
      invokeCount += 1;
      return JSON.stringify({});
    },
  });

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-no-main-success",
      turn_type: "main",
      session_done: true,
      success: false,
      messages: [
        { role: "user", content: "Do something risky." },
        { role: "assistant", content: "I failed." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "skipped");
  assert.equal(result.jobs?.[0]?.reason, "no_successful_main_turn");
  assert.equal(invokeCount, 0);
  assert.equal(listSkillDirs(paths.skillBankDir, "user1").length, 0);
});

test("embedded runtime finalizes previous session when session_id changes for same user", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    invokeModel: makeInvokeModelForAdd(),
  });

  const first = await processor.handle(
    {
      user: "user1",
      session_id: "sess-A",
      turn_type: "main",
      session_done: false,
      success: true,
      messages: [
        { role: "user", content: "Need better release routine." },
        { role: "assistant", content: "Use a strict checklist." },
      ],
    },
    {},
    {},
  );
  assert.equal(first.status, "skipped");
  assert.equal(first.reason, "session_not_finished");

  const switched = await processor.handle(
    {
      user: "user1",
      session_id: "sess-B",
      turn_type: "side",
      session_done: false,
      success: true,
      messages: [{ role: "user", content: "New conversation starts." }],
    },
    {},
    {},
  );
  assert.equal(switched.status, "scheduled");
  assert(switched.jobs.some((job) => job.session_id === "sess-A"));
  assert.equal(listSkillDirs(paths.skillBankDir, "user1").length, 1);
});

test("embedded runtime skips internal extraction events to prevent recursion", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  let invokeCount = 0;
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    async invokeModel() {
      invokeCount += 1;
      return JSON.stringify({});
    },
  });

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-internal",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [{ role: "user", content: "Internal test" }],
    },
    { autoskill_internal: true },
    {},
  );

  assert.equal(result.status, "skipped");
  assert.equal(result.reason, "internal_extraction_event");
  assert.equal(invokeCount, 0);
});

test("embedded runtime keeps skills in SkillBank without mirroring when install mode is store_only", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(
    makeConfig(paths, { skillInstallMode: "store_only" }),
    {},
    logger,
    {
      invokeModel: makeInvokeModelForAdd(),
    },
  );

  const done = await processor.handle(
    {
      user: "user1",
      session_id: "sess-store-only",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Please teach me release routine." },
        { role: "assistant", content: "Use a reusable checklist." },
      ],
    },
    {},
    {},
  );

  assert.equal(done.status, "scheduled");
  const job = done.jobs.find((item) => item.status === "added");
  assert.ok(job);
  assert.equal(job.mirror_skipped, true);
  assert.equal(job.mirror_reason, "install_mode_store_only");

  const userSkillDirs = listSkillDirs(paths.skillBankDir, "user1");
  assert.equal(userSkillDirs.length, 1);
  const skillDirName = userSkillDirs[0].name;
  assert.ok(fs.existsSync(path.join(paths.skillBankDir, "Users", "user1", skillDirName, "SKILL.md")));
  assert.equal(fs.existsSync(path.join(paths.openclawSkillsDir, skillDirName, "SKILL.md")), false);
});

test("embedded runtime writes single-line frontmatter-safe metadata for generated SKILL.md", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(makeConfig(paths), {}, logger, {
    invokeModel: makeInvokeModelWithMultilineMetadata(),
  });

  const done = await processor.handle(
    {
      user: "user1",
      session_id: "sess-frontmatter",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need a reusable release policy." },
        { role: "assistant", content: "Will prepare one." },
      ],
    },
    {},
    {},
  );

  assert.equal(done.status, "scheduled");
  const added = done.jobs.find((job) => job.status === "added");
  assert.ok(added?.path);

  const md = fs.readFileSync(String(added.path), "utf8");
  const frontmatter = md.split("\n---\n")[0];
  assert.match(frontmatter, /name: "Release Checklist \\"Pro\\""/);
  assert.match(frontmatter, /description: "Reusable release checklist for deployment workflows\."/);
  assert.match(frontmatter, /  - "deployment checks"/);
  assert.match(frontmatter, /  - "ops core"/);
});

test("embedded runtime falls back to runtime-resolved HTTP target when direct runtime invoke fails", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const calls = [];
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime"],
          timeoutMs: 5000,
          retries: 0,
        },
      },
    }),
    {
      runtime: {
        async invokeModel() {
          throw new Error("runtime direct invoke failed");
        },
        model: {
          base_url: "http://runtime-fallback.local",
          api_key: "runtime-key",
          model: "runtime-model",
        },
      },
    },
    logger,
    {
      requestJson: makeHttpModelResponder(calls),
    },
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-runtime-http",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need reusable trajectory skill." },
        { role: "assistant", content: "I will build one." },
      ],
    },
    { model: "runtime-model" },
    {},
  );

  assert.equal(result.status, "scheduled");
  assert(result.jobs.some((job) => job.status === "added"));
  assert(calls.some((item) => item.url === "http://runtime-fallback.local/v1/chat/completions"));
});

test("embedded runtime falls back to openclaw-config-resolve mode when runtime modes are unavailable", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const openclawHome = path.join(paths.root, "openclaw-home");
  fs.mkdirSync(openclawHome, { recursive: true });
  fs.writeFileSync(
    path.join(openclawHome, "openclaw.json"),
    JSON.stringify({
      llm: {
        provider: "openai",
        model: "cfg-model",
        base_url: "http://cfg-fallback.local",
        api_key_env: "CFG_FALLBACK_KEY",
      },
    }),
    "utf8",
  );
  process.env.CFG_FALLBACK_KEY = "cfg-key";
  const calls = [];
  try {
    const processor = createEmbeddedProcessor(
      makeConfig(paths, {
        embedded: {
          modelInvocation: {
            modes: ["openclaw-runtime", "openclaw-config-resolve"],
            openclawHome,
            timeoutMs: 5000,
            retries: 0,
          },
        },
      }),
      {},
      logger,
      {
        requestJson: makeHttpModelResponder(calls),
      },
    );

    const result = await processor.handle(
      {
        user: "user1",
        session_id: "sess-config-resolve",
        turn_type: "main",
        session_done: true,
        success: true,
        messages: [
          { role: "user", content: "Need a reusable config-derived skill." },
          { role: "assistant", content: "Working on it." },
        ],
      },
      { model: "cfg-model" },
      {},
    );

    assert.equal(result.status, "scheduled");
    assert(result.jobs.some((job) => job.status === "added"));
    assert(calls.some((item) => item.url === "http://cfg-fallback.local/v1/chat/completions"));
  } finally {
    delete process.env.CFG_FALLBACK_KEY;
  }
});

test("embedded runtime falls back to manual mode when runtime and config-resolve are unavailable", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const calls = [];
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime", "openclaw-config-resolve", "manual"],
          manualBaseUrl: "http://manual-fallback.local",
          manualApiKey: "manual-key",
          manualModel: "manual-model",
          timeoutMs: 5000,
          retries: 0,
        },
      },
    }),
    {},
    logger,
    {
      requestJson: makeHttpModelResponder(calls),
    },
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-manual",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need a manual fallback skill." },
        { role: "assistant", content: "Will add one." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "scheduled");
  assert(result.jobs.some((job) => job.status === "added"));
  assert(calls.some((item) => item.url === "http://manual-fallback.local/v1/chat/completions"));
});

test("embedded runtime can use runtime subagent invocation mode", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime-subagent"],
          timeoutMs: 5000,
          retries: 0,
        },
      },
    }),
    {
      async runSubAgent({ metadata }) {
        if (metadata?.channel === "autoskill_embedded_extract") {
          return JSON.stringify({
            skills: [
              {
                name: "Subagent Skill",
                description: "Extracted via runtime subagent.",
                prompt: "Step 1\nStep 2",
                triggers: ["subagent path"],
                tags: ["runtime"],
              },
            ],
          });
        }
        if (metadata?.channel === "autoskill_embedded_maintain") {
          return JSON.stringify({ action: "add" });
        }
        return JSON.stringify({});
      },
    },
    logger,
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-subagent",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need subagent extraction." },
        { role: "assistant", content: "Sure." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "scheduled");
  assert(result.jobs.some((job) => job.status === "added"));
});

test("embedded runtime stays fail-open when all model invocation modes fail", async () => {
  const paths = makeSandbox();
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime", "openclaw-runtime-subagent", "openclaw-config-resolve", "manual"],
          openclawHome: path.join(paths.root, "missing-home"),
          manualBaseUrl: "",
        },
      },
    }),
    {},
    logger,
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-all-fail",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need robust fail-open behavior." },
        { role: "assistant", content: "Try extraction." },
      ],
    },
    {},
    {},
  );

  assert.equal(result.status, "skipped");
  assert.equal(result.reason, "session_not_extractable");
  assert.equal(result.jobs?.[0]?.status, "failed");
});

test("embedded runtime maintenance merges into explicit target skill in subagent mode", async () => {
  const paths = makeSandbox();
  writeExistingSkill({
    skillBankDir: paths.skillBankDir,
    dirName: "release-existing",
    name: "Release Existing",
    prompt: "Run smoke tests.\nPublish release notes.",
  });
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime-subagent"],
        },
      },
    }),
    {
      async runSubAgent({ metadata, user }) {
        if (metadata?.channel === "autoskill_embedded_extract") {
          return JSON.stringify({
            skills: [
              {
                name: "Release Existing",
                description: "Improved release routine.",
                prompt: "Run smoke tests.\nPublish release notes.\nAdd rollback checks.",
                triggers: ["release"],
                tags: ["ops"],
              },
            ],
          });
        }
        if (metadata?.channel === "autoskill_embedded_maintain") {
          const parsed = JSON.parse(String(user || "{}"));
          const targetId = parsed?.similar_skills?.[0]?.id || "release-existing";
          return JSON.stringify({ action: "merge", target_skill_id: targetId });
        }
        if (metadata?.channel === "autoskill_embedded_merge") {
          return JSON.stringify({
            name: "Release Existing",
            description: "Merged release routine",
            prompt: "Run smoke tests.\nPublish release notes.\nAdd rollback checks.",
            triggers: ["release workflow"],
            tags: ["ops", "release"],
          });
        }
        return JSON.stringify({});
      },
    },
    logger,
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-maintain-merge",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need a reusable release workflow." },
        { role: "assistant", content: "Will maintain it." },
      ],
    },
    {},
    {},
  );

  const mergedJob = result.jobs.find((job) => job.status === "merged");
  assert.ok(mergedJob);
  assert.equal(mergedJob.skill_id, "release-existing");
  const md = fs.readFileSync(String(mergedJob.path), "utf8");
  assert.match(md, /version: "0.1.1"/);
  assert.match(md, /Add rollback checks\./);
});

test("embedded runtime merge preserves candidate bundled resources when prompt is otherwise unchanged", async () => {
  const paths = makeSandbox();
  writeExistingSkill({
    skillBankDir: paths.skillBankDir,
    dirName: "release-existing",
    name: "Release Existing",
    description: "Reusable release routine.",
    prompt: "Run smoke tests.\nPublish release notes.",
  });
  const logger = makeLogger();
  let maintainCallCount = 0;
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime-subagent"],
        },
      },
    }),
    {
      async runSubAgent({ metadata, user }) {
        if (metadata?.channel === "autoskill_embedded_extract") {
          return JSON.stringify({
            skills: [
              {
                name: "Release Existing",
                description: "Reusable release routine.",
                prompt: "Run smoke tests.\nPublish release notes.",
                triggers: ["release workflow"],
                tags: ["ops"],
                files: {
                  "references/release-checks.md": "# Checks\n- verify rollback plan\n",
                },
              },
            ],
          });
        }
        if (metadata?.channel === "autoskill_embedded_maintain") {
          maintainCallCount += 1;
          const parsed = JSON.parse(String(user || "{}"));
          return JSON.stringify({ action: "merge", target_skill_id: parsed?.similar_skills?.[0]?.id || "release-existing" });
        }
        if (metadata?.channel === "autoskill_embedded_merge") {
          return JSON.stringify({
            name: "Release Existing",
            description: "Reusable release routine.",
            prompt: "Run smoke tests.\nPublish release notes.",
            triggers: ["release workflow"],
            tags: ["ops"],
          });
        }
        return JSON.stringify({});
      },
    },
    logger,
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-merge-files",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need the release routine with a reusable checks file." },
        { role: "assistant", content: "Will update the existing skill." },
      ],
    },
    {},
    {},
  );

  assert.equal(maintainCallCount, 1);
  const merged = result.jobs.find((job) => job.status === "merged");
  assert.ok(merged?.path);
  const skillDir = path.dirname(String(merged.path));
  assert.equal(fs.existsSync(path.join(skillDir, "references", "release-checks.md")), true);
  const md = fs.readFileSync(String(merged.path), "utf8");
  assert.match(md, /`references\/release-checks\.md`/);
});

test("embedded runtime maintenance avoids unsafe merge target and falls back to add", async () => {
  const paths = makeSandbox();
  writeExistingSkill({
    skillBankDir: paths.skillBankDir,
    dirName: "finance-existing",
    name: "Finance Routine",
    prompt: "Compute quarterly revenue growth.\nReport metrics.",
  });
  const logger = makeLogger();
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime-subagent"],
        },
      },
    }),
    {
      async runSubAgent({ metadata }) {
        if (metadata?.channel === "autoskill_embedded_extract") {
          return JSON.stringify({
            skills: [
              {
                name: "Cooking Prep",
                description: "Kitchen prep workflow.",
                prompt: "Wash vegetables.\nPreheat oven.\nSet timer.",
                triggers: ["cook dinner"],
                tags: ["kitchen"],
              },
            ],
          });
        }
        if (metadata?.channel === "autoskill_embedded_maintain") {
          return JSON.stringify({ action: "merge", target_skill_id: "not-exists" });
        }
        return JSON.stringify({});
      },
    },
    logger,
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-maintain-safe-add",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need a reusable cooking prep routine." },
        { role: "assistant", content: "Will create one." },
      ],
    },
    {},
    {},
  );

  const added = result.jobs.find((job) => job.status === "added");
  assert.ok(added);
  assert.notEqual(added.skill_id, "finance-existing");
});

test("embedded runtime maintenance skips duplicate candidate without merge/add", async () => {
  const paths = makeSandbox();
  writeExistingSkill({
    skillBankDir: paths.skillBankDir,
    dirName: "dup-existing",
    name: "Duplicate Skill",
    description: "Duplicate of existing skill.",
    prompt: "Collect logs.\nRun diagnostics.\nSummarize findings.",
    triggers: ["diagnose issue"],
    tags: ["ops"],
  });
  const logger = makeLogger();
  let maintainCallCount = 0;
  const processor = createEmbeddedProcessor(
    makeConfig(paths, {
      embedded: {
        modelInvocation: {
          modes: ["openclaw-runtime-subagent"],
        },
      },
    }),
    {
      async runSubAgent({ metadata }) {
        if (metadata?.channel === "autoskill_embedded_extract") {
          return JSON.stringify({
            skills: [
              {
                name: "Duplicate Skill",
                description: "Duplicate of existing skill.",
                prompt: "Collect logs.\nRun diagnostics.\nSummarize findings.",
                triggers: ["diagnose issue"],
                tags: ["ops"],
              },
            ],
          });
        }
        if (metadata?.channel === "autoskill_embedded_maintain") {
          maintainCallCount += 1;
          return JSON.stringify({ action: "add" });
        }
        return JSON.stringify({});
      },
    },
    logger,
  );

  const result = await processor.handle(
    {
      user: "user1",
      session_id: "sess-duplicate-skip",
      turn_type: "main",
      session_done: true,
      success: true,
      messages: [
        { role: "user", content: "Need diagnostics routine." },
        { role: "assistant", content: "Will extract one." },
      ],
    },
    {},
    {},
  );

  const skipped = result.jobs.find((job) => job.reason === "duplicate_existing_skill");
  assert.ok(skipped);
  assert.equal(maintainCallCount, 0);
});
