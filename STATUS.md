# STATUS

## 2026-03-15 - Round 31 (remove accidental GitHub workflow delivery)

### Scope
- Target area: `.github/workflows/autoskill4openclaw-ci.yml`.
- Objective: remove the GitHub Actions workflow that was added during delivery hardening but should not be part of the submitted OpenClaw plugin changes.

### Completed
- Removed `.github/workflows/autoskill4openclaw-ci.yml` from the repository.
- Kept all AutoSkill4OpenClaw code, tests, docs, and runtime changes intact.

### Validation
- Executed:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `62/62` Python tests pass.
  - `60/60` adapter tests pass.

### Self-Review Notes
- This round only removed repository-level CI metadata and did not change runtime behavior, plugin hooks, extraction logic, or documentation outside the status log.

### Remaining Issues / Risks
- Embedded mode still depends on the host OpenClaw deployment actually executing lifecycle hooks such as `before_prompt_build` and `agent_end`.
- The runtime still depends on a local repository checkout and is not yet packaged as a standalone distributable for `AutoSkill4OpenClaw`.
- Mirrored skill identity/conflict protection can still be hardened further before enabling more aggressive automated pruning or overwrite behavior.

### Next Step
- Continue with delivery-focused runtime hardening only:
  - add mirrored-skill conflict guardrails
  - add one lightweight real-runtime smoke scenario for OpenClaw deployment boundaries
  - keep pruning/cleanup logic conservative and fail-open

## 2026-03-15 - Round 30 (delivery hardening: CI, entrypoint smoke tests, and top-level docs)

### Scope
- Target area: `AutoSkill4OpenClaw/tests/test_install.py`, `AutoSkill4OpenClaw/README.md`, `AutoSkill4OpenClaw/README.zh-CN.md`, top-level `README.md`, and CI coverage.
- Objective: tighten delivery confidence by verifying entrypoint scripts actually start, clarifying runtime prerequisites/checkout assumptions, and aligning the top-level project documentation with the current embedded-first OpenClaw integration path.

### Completed
- Added CLI smoke coverage in `AutoSkill4OpenClaw/tests/test_install.py`:
  - `install.py --help` must execute successfully
  - `run_proxy.py --help` must execute successfully
  - this guards against import-path regressions and broken entrypoint wiring that unit tests alone could miss
- Improved plugin READMEs:
  - documented that Node.js is only needed for adapter tests / local verification scripts
  - documented that `curl` is only needed for the optional sidecar verification script
  - documented that the local repository checkout must remain on disk after installation because runtime scripts still reference `AutoSkill4OpenClaw/run_proxy.py`
- Updated top-level `README.md`:
  - repository structure now describes `AutoSkill4OpenClaw/` as embedded-first OpenClaw integration instead of a sidecar-only plugin
  - the OpenClaw quick-install example now reflects the recommended embedded-first path
  - top-level docs now explicitly state that the sidecar path is optional and not required for the recommended mainline
- Added lightweight GitHub Actions coverage in `.github/workflows/autoskill4openclaw-ci.yml`:
  - install package with `pip install -e .`
  - run `python -m unittest discover -s AutoSkill4OpenClaw/tests -q`
  - run `npm test` in `AutoSkill4OpenClaw/adapter`

### Validation
- Executed:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - `python3 -m compileall AutoSkill4OpenClaw`
- Result:
  - `62/62` Python tests pass.
  - `60/60` adapter tests pass.
  - `compileall` passes for `AutoSkill4OpenClaw`.

### Self-Review Notes
- This round stayed low-risk:
  - no extraction/runtime behavior changed
  - no OpenClaw hook logic changed
  - no memory/tool/provider path changed
- The new CI/workflow coverage is intentionally narrow and focused on the OpenClaw integration surface instead of trying to validate the whole repository at once.

### Remaining Issues / Risks
- Embedded mode still depends on the host OpenClaw deployment actually executing lifecycle hooks such as `before_prompt_build` and `agent_end`.
- The runtime still depends on a local repository checkout and is not yet packaged as a standalone distributable for `AutoSkill4OpenClaw`.
- Mirrored skill identity/conflict protection can still be hardened further before enabling more aggressive automated pruning or overwrite behavior.

### Next Step
- Continue with final delivery-risk reduction:
  - add mirrored-skill conflict guardrails
  - add one lightweight real-runtime smoke scenario for OpenClaw deployment boundaries
  - keep pruning/cleanup logic conservative and fail-open

## 2026-03-15 - Round 29 (pre-delivery env and naming audit)

### Scope
- Target area: `AutoSkill4OpenClaw/.env.example`, `AutoSkill4OpenClaw/install.py`, `AutoSkill4OpenClaw/tests/test_install.py`, and plugin README naming/compatibility notes.
- Objective: close pre-delivery gaps around environment-template drift, false-positive coverage tests, and naming clarity between the repo, adapter id, and sidecar runtime install paths.

### Completed
- Fixed environment template drift:
  - refreshed `AutoSkill4OpenClaw/.env.example` so it includes the full current AutoSkill/OpenClaw adapter env surface instead of only the older reduced subset
  - added embedded runtime envs such as:
    - `AUTOSKILL_OPENCLAW_RUNTIME_MODE`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_SESSION_DIR`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_SESSION_MAX_TURNS`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_MODES`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_*`
  - added compatibility/fallback envs used by adapter code such as:
    - `AUTOSKILL_BASE_URL`
    - `AUTOSKILL_PROXY_BASE_URL`
    - `AUTOSKILL_DOTENV`
    - `AUTOSKILL_MAX_INJECTED_CHARS`
    - `AUTOSKILL_SKILLBANK_DIR`
    - `AUTOSKILL_REPO_SKILLBANK_DIR`
    - `AUTOSKILL_PROXY_MODELS`
- Fixed generated installer `.env` output in `AutoSkill4OpenClaw/install.py` so fresh installs receive the same expanded env surface as the checked-in example file.
- Tightened regression coverage in `AutoSkill4OpenClaw/tests/test_install.py`:
  - the env-example audit now parses exact env keys instead of using substring matching
  - the audit now checks env usage across `run_proxy.py`, `adapter/index.js`, and `adapter/embedded_runtime.js`
  - this closes a real false-positive gap where `AUTOSKILL_PROXY_MODELS` was previously considered covered by `AUTOSKILL_PROXY_MODELS_JSON`
- Improved naming clarity in both plugin READMEs:
  - documented that the repo/project name is `AutoSkill4OpenClaw`
  - documented that the adapter id remains `autoskill-openclaw-adapter`
  - documented that the optional sidecar runtime install dir remains `~/.openclaw/plugins/autoskill-openclaw-plugin`
  - explicitly called out that these runtime/install identifiers are retained for compatibility

### Validation
- Executed:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `60/60` Python tests pass.
  - `60/60` adapter tests pass.

### Self-Review Notes
- This round intentionally focused on low-risk delivery hardening:
  - no runtime extraction logic changed
  - no OpenClaw hook behavior changed
  - no memory/provider/tool path changed
- The env-template/test fix matters because it catches drift that would otherwise only appear during deployment or manual configuration.

### Remaining Issues / Risks
- Embedded mode still depends on the host OpenClaw deployment actually executing lifecycle hooks such as `before_prompt_build` and `agent_end`.
- The repository still assumes a local checkout for AutoSkill4OpenClaw runtime scripts rather than packaging it as a standalone Python distribution module.
- Mirrored skill identity/conflict protection can still be hardened further before enabling any more aggressive automated pruning.

### Next Step
- Continue with delivery-focused hardening:
  - add stronger mirrored-skill conflict guardrails
  - add a lightweight real-runtime smoke check
  - keep usage-based pruning conservative and fail-open

## 2026-03-15 - Round 28 (installer and schema alignment for embedded mainline)

### Scope
- Target area: `AutoSkill4OpenClaw/install.py`, `AutoSkill4OpenClaw/.env.example`, `AutoSkill4OpenClaw/adapter/openclaw.plugin.json`, and plugin README alignment.
- Objective: close delivery gaps where the documented embedded-first setup was not fully reflected in installer defaults, environment templates, or plugin config schema.

### Completed
- Fixed installer defaults in `AutoSkill4OpenClaw/install.py`:
  - `openclaw.json` upsert now writes embedded-first defaults when values are absent:
    - `runtimeMode=embedded`
    - `openclawSkillInstallMode=openclaw_mirror`
    - embedded directories for `skillBankDir`, `openclawSkillsDir`, and `sessionArchiveDir`
    - `embedded.sessionMaxTurns=20`
  - installer now creates `~/.openclaw/autoskill/embedded_sessions`
  - generated `.env` template now includes `AUTOSKILL_OPENCLAW_SESSION_MAX_TURNS=20`
  - installer wording now describes the runtime/adapter installation more accurately instead of calling it only a sidecar installer
- Fixed plugin schema drift in `AutoSkill4OpenClaw/adapter/openclaw.plugin.json`:
  - added missing `embedded.sessionMaxTurns`
  - added missing `embedded.promptPackPath`
  - refreshed adapter description so it reflects embedded + sidecar support
- Unified bare adapter defaults with the embedded-first product path:
  - `AutoSkill4OpenClaw/adapter/index.js` now defaults `runtimeMode` to `embedded`
  - `AutoSkill4OpenClaw/adapter/openclaw.plugin.json` now defaults `runtimeMode` to `embedded`
  - `store_only` remains the explicit exception: retrieval auto-injection is still enabled there even under embedded runtime, so non-mirrored setups keep the expected behavior
- Refreshed `AutoSkill4OpenClaw/.env.example` so it matches current runtime options instead of an older reduced variable set.
- Updated plugin READMEs:
  - installer behavior is now documented as writing embedded-first defaults automatically
  - users only need manual edits for overrides or sidecar switching
- Added regression coverage in `AutoSkill4OpenClaw/tests/test_install.py`:
  - installer writes embedded defaults
  - existing explicit runtime/install choices are preserved
  - env template includes long-session turn limit
  - `.env.example` stays aligned with `run_proxy.py` env keys
  - plugin manifest schema exposes embedded fields used by code/docs

### Validation
- Executed:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - `python3 -m compileall AutoSkill4OpenClaw`
- Result:
  - `60/60` Python tests pass.
  - `60/60` adapter tests pass.
  - `compileall` passes for `AutoSkill4OpenClaw`.

### Self-Review Notes
- This round now aligns both installer behavior and bare adapter defaults with the documented embedded-first path, while still preserving explicit user choices already present in `openclaw.json`.
- Existing explicit `runtimeMode=sidecar` and `openclawSkillInstallMode=store_only` values are preserved by the installer.

### Remaining Issues / Risks
- The repository still assumes a local checkout for AutoSkill4OpenClaw runtime scripts rather than packaging it as a standalone Python distribution module.
- Embedded mode still depends on the host OpenClaw deployment actually executing lifecycle hooks such as `before_prompt_build` and `agent_end`; AutoSkill now has better diagnostics for this, but it cannot force a non-hooked execution path to emit extraction events.

### Next Step
- Continue with a focused delivery audit:
  - audit skill identity/conflict handling for mirrored installs
  - tighten docs around hook-trigger troubleshooting and deployment boundaries
  - consider a lightweight end-to-end smoke check for real OpenClaw runtime paths

## 2026-03-15 - Round 27 (long-session auto-checkpoint after 20 turns)

### Scope
- Target area: `AutoSkill4OpenClaw/openclaw_conversation_archive.py`, `AutoSkill4OpenClaw/adapter/embedded_runtime.js`, and related config/docs/tests.
- Objective: avoid waiting forever when `session_id` never changes by auto-closing a long-lived session segment after a safe turn threshold and running one extraction/maintenance pass.

### Completed
- Added a new session turn-limit safeguard to both runtime paths:
  - Python sidecar/session-end archive path now supports `session_max_turns` in `OpenClawConversationArchiveConfig`
  - embedded runtime now supports `embedded.sessionMaxTurns`
- Set the default threshold to `20` turns on both paths:
  - sidecar env/CLI: `AUTOSKILL_OPENCLAW_SESSION_MAX_TURNS` / `--openclaw-session-max-turns`
  - embedded adapter config/env: `embedded.sessionMaxTurns` / `AUTOSKILL_OPENCLAW_EMBEDDED_SESSION_MAX_TURNS`
- Implemented auto-close behavior:
  - when the archived turn count for the active session reaches the threshold, the current session segment is finalized with reason `session_turn_limit`
  - extraction/maintenance then runs on that closed segment instead of waiting forever for `session_done` or a session id change
  - active in-memory bookkeeping is cleared so the next turn with the same `session_id` starts a fresh segment
- Hardened observability:
  - returned/logged session path now points to the finalized closed file after turn-limit close, instead of the pre-rename live path
- Updated docs in both plugin READMEs to explain:
  - the new `20`-turn default
  - how to disable it by setting the value to `0`
  - where the setting lives in embedded vs sidecar mode
- Added regression coverage:
  - `AutoSkill4OpenClaw/tests/test_conversation_archive.py`
  - `AutoSkill4OpenClaw/tests/test_service_runtime.py`
  - `AutoSkill4OpenClaw/tests/test_run_proxy_defaults.py`
  - `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
- Result:
  - `59/59` adapter tests pass.
  - `55/55` Python tests pass.

### Self-Review Notes
- The threshold is intentionally segment-based, not global-session destructive truncation: once a long session segment is closed, the next turn with the same `session_id` starts a new local segment cleanly.
- This is fail-open relative to conversation continuity: it never blocks the live OpenClaw turn; it only affects when AutoSkill decides that the archived evidence is sufficient to attempt extraction.
- No memory slot, compaction, provider routing, or OpenClaw core behavior was changed.

### Remaining Issues / Risks
- A very long multi-topic session can now produce multiple extraction passes instead of a single session-end pass. This is usually preferable to waiting forever, but it can increase maintenance frequency on noisy sessions.
- The threshold is a simple turn count today. A future improvement could combine turn count with topic-change heuristics or inactivity signals for cleaner segmentation.

### Next Step
- Add one more safety layer for generated skill installation:
  - audit name/identity conflicts between generated SkillBank skills and existing OpenClaw local/native skills
  - prefer stable conflict detection before considering more aggressive automated pruning

## 2026-03-15 - Round 26 (feedback + session-evidence extraction inputs)

### Scope
- Target area: `AutoSkill4OpenClaw/service_runtime.py` and `AutoSkill4OpenClaw/adapter/embedded_runtime.js`.
- Objective: improve extraction quality by preserving explicit end-of-session user feedback and by giving the embedded extractor explicit session-level evidence about `main` turns and success state.

### Completed
- Audited current extraction-input paths and confirmed a real gap:
  - `agent_end` already receives `user_feedback`, but the session-end extraction path was only archiving raw messages and silently dropping the feedback from the later extraction window.
  - embedded extraction prompts required `turn_type=main` evidence, but the extractor only saw merged `session_messages`, not explicit turn summaries or main/success evidence.
- Fixed session-end feedback loss in `AutoSkill4OpenClaw/service_runtime.py`:
  - added `_append_user_feedback_message(...)`
  - archived conversation records now append explicit `user_feedback` as a final user message when it adds new evidence
  - session archive records now do the same, so session-end extraction keeps the strongest user-supplied supervision signal
- Improved embedded extraction inputs in `AutoSkill4OpenClaw/adapter/embedded_runtime.js`:
  - session archiving now preserves `payload.user_feedback` in the closed session transcript
  - `loadClosedSession(...)` now builds compact `session_evidence`:
    - `session_id`
    - `closed_reason`
    - `turn_count`
    - `has_main_turn`
    - `has_successful_main_turn`
    - per-turn summaries: `turn_index`, `turn_type`, `success`, `message_count`, `roles`
  - `extractCandidate(...)` now passes `session_evidence` into the extractor payload instead of relying only on the flattened message list
- Updated shared prompt guidance in `AutoSkill4OpenClaw/adapter/openclaw_prompt_pack.txt` so the embedded extractor explicitly uses `session_evidence` when present.
- Added regression coverage:
  - `AutoSkill4OpenClaw/tests/test_service_runtime.py`
    - verifies `user_feedback` is preserved in both archived session data and the scheduled extraction window
  - `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`
    - verifies extractor input contains explicit feedback text and `session_evidence`

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
- Result:
  - `57/57` adapter tests pass.
  - `53/53` Python tests pass.

### Self-Review Notes
- This round improves only extraction input fidelity; it does not change retrieval injection, memory behavior, provider/model routing, or OpenClaw core execution.
- The feedback append is deduplicated against the last user message to avoid obvious duplicate tails.
- `session_evidence` is intentionally compact and summary-only, so it improves model grounding without duplicating the full transcript payload.

### Remaining Issues / Risks
- Embedded/session-end extraction is now better grounded, but it still operates on a whole-session view, which is intentionally different from the sidecar main-turn proxy’s `main-turn + assistant + next_state` sampling granularity.
- Explicit user feedback is now preserved only when it is passed in the hook payload; if upstream channels never populate `user_feedback`, we still depend on the normal message trajectory for supervision.

### Next Step
- Reconcile and document the strengths/limits of the two extraction timings more explicitly:
  - embedded/session-end extraction for convenience and stable OpenClaw-native skill evolution
  - sidecar/main-turn sampling for finer-grained trajectory learning and RL-style data collection

## 2026-03-15 - Round 25 (embedded bundled-resource preservation)

### Scope
- Target area: `AutoSkill4OpenClaw/adapter/embedded_runtime.js` and prompt pack alignment.
- Objective: close the gap between OpenClaw standard skill artifacts and the embedded runtime by preserving extracted `scripts/`, `references/`, and `assets/` instead of dropping them.

### Completed
- Audited OpenClaw skill loading/authoring expectations against the current embedded runtime:
  - confirmed OpenClaw standard skills are directory artifacts with `SKILL.md` plus optional bundled resources.
  - confirmed AutoSkill embedded prompts already encouraged resources, but embedded write-paths were silently discarding them.
- Implemented bundled resource support in `AutoSkill4OpenClaw/adapter/embedded_runtime.js`:
  - added safe normalization for extracted resource paths under `scripts/`, `references/`, and `assets/`
  - added flexible parsing for optional `files/resources` payloads from extractor/merge model outputs
  - preserved bundled resources on add/merge writes into SkillBank
  - rendered `## Files` in generated `SKILL.md`
  - loaded existing resource files back from SkillBank during maintenance/BM25 matching
  - included resource paths in duplicate detection so "same prompt but new reusable files" is no longer skipped
  - preserved candidate resources during merge even when the merge LLM returns only metadata/prompt fields
- Tightened embedded prompt pack alignment in `AutoSkill4OpenClaw/adapter/openclaw_prompt_pack.txt`:
  - embedded extraction now explicitly allows concise optional resources/files
  - embedded merge now explicitly preserves bundled resources when they improve the same capability
- Updated embedded docs:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
  - both now explicitly state that generated skills can keep bundled resources in SkillBank and in the OpenClaw mirror
- Added regression coverage in `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`:
  - extracted bundled resources are written to SkillBank and mirrored to OpenClaw
  - merge keeps candidate bundled resources even if the merge LLM omits them
  - duplicate skip test now reflects a true metadata-identical duplicate instead of a candidate with different retrieval metadata

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
- Result:
  - `56/56` adapter tests pass.
  - `52/52` Python tests pass.

### Failed Attempts
- Initial implementation treated any richer candidate description as a meaningful delta, which broke the duplicate-skip regression. Tightened the logic so description-only wording changes no longer bypass duplicate detection.
- Initial merge implementation still lost candidate resources when the merge LLM returned JSON without `files`. Fixed by merging `existing.files + candidate.files` into the normalization fallback.

### Self-Review Notes
- This round is intentionally localized to the embedded runtime and shared prompt pack; it does not modify OpenClaw core, memory behavior, provider/model routing, hook registration, or sidecar transport.
- Resource paths are constrained to safe relative paths under `scripts/`, `references/`, or `assets/`.
- The write-path remains fail-open: if no resources are extracted, behavior stays equivalent to the previous `SKILL.md`-only flow.

### Remaining Issues / Risks
- Embedded maintenance now reads existing resource files from SkillBank for matching/preservation, which is correct but adds extra filesystem work per maintenance cycle; it may need a stricter cap if users maintain very large manual skills.
- Binary assets are intentionally preserved on disk once written, but embedded maintenance only reads small text-like files back into memory; binary-heavy skills may need a lighter manifest-only path later.

### Next Step
- Revisit embedded maintenance scoring/prompts with full OpenClaw skill authoring semantics in mind:
  - decide whether bundled resource paths should also influence add-vs-merge prompting more explicitly
  - evaluate whether usage-count / stale-skill pruning can safely incorporate mirrored resource-heavy skills without false deletions

## 2026-03-15 - Round 24 (embedded install docs without provider args)

### Scope
- Target area: `AutoSkill4OpenClaw/README.md` and `AutoSkill4OpenClaw/README.zh-CN.md`.
- Objective: make the recommended embedded installation path explicit and remove the impression that users must provide separate LLM/embedding providers.

### Completed
- Reworked the install section in both plugin READMEs:
  - added a dedicated "recommended embedded install" subsection
  - installation command now omits `--llm-provider`, `--llm-model`, `--embeddings-provider`, and `--embeddings-model`
  - clarified that embedded mode reuses the existing OpenClaw runtime/model path
  - clarified that generated `.env` provider placeholders are optional in embedded mode
  - clarified that the sidecar process does not need to be started for the recommended embedded path
- Kept an explicit optional subsection for sidecar/manual-provider installation so advanced deployments still have a documented path.

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `54/54` adapter tests pass.

### Self-Review Notes
- Docs now match the actual embedded runtime direction: installation is lightweight and does not require users to choose a separate provider stack up front.
- No code-path changes were introduced in this round.

## 2026-03-14 - Round 23 (message_received diagnostics for Feishu ingress)

### Scope
- Target area: `AutoSkill4OpenClaw/adapter/index.js`.
- Objective: distinguish "channel traffic reached plugin hooks" from "agent lifecycle hooks executed" in Feishu/OpenClaw deployments.

### Completed
- Added a low-risk diagnostic probe on `message_received`:
  - registers `message_received` alongside existing `before_prompt_build` and `agent_end` hooks.
  - logs first invocation marker:
    - `hook first invocation name=message_received`
  - logs per-event session/channel summary without dumping prompt bodies:
    - `message_received invoked session=... channel=...`
- Extended lifecycle watchdog logging:
  - now reports `message_received`, `before_prompt_build`, and `agent_end` counters together.
  - makes it easy to tell whether Feishu traffic hits plugin hooks at all, or only stops before agent loop.
- Updated adapter tests in `AutoSkill4OpenClaw/adapter/index.test.mjs`:
  - registration list now includes `message_received`
  - diagnostics test now verifies first-invocation and session/channel logging for `message_received`

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `54/54` adapter tests pass.

### Self-Review Notes
- This change is diagnostic-only and fail-open.
- No message mutation, retrieval behavior, memory behavior, or provider/model path was changed.

### Remaining Issues / Risks
- If `message_received` still does not fire in production, the issue is below plugin lifecycle registration and likely in deployment/load/runtime boundaries.
- If `message_received` fires but `before_prompt_build` does not, the message is entering channel dispatch but not reaching `runEmbeddedPiAgent(...)`.

## 2026-03-14 - Round 22 (main-turn proxy turn-type inference parity)

### Scope
- Target area: `AutoSkill4OpenClaw/openclaw_main_turn_proxy.py`.
- Objective: align sidecar main-turn proxy sampling with the embedded fallback when OpenClaw omits explicit `turn_type`.

### Completed
- Audited `OpenClaw-RL` proxy sampling flow against local plugin code:
  - confirmed `OpenClaw-RL` collects data from `/v1/chat/completions` proxy traffic and buffers previous `main` turn until the next request provides `next_state`.
  - confirmed local embedded path is session-close extraction and not equivalent to RL proxy sampling.
- Fixed sidecar proxy parsing in `AutoSkill4OpenClaw/openclaw_main_turn_proxy.py`:
  - added `infer_turn_type_from_messages(...)`.
  - `parse_turn_context(...)` now falls back to message-based inference when `X-Turn-Type` / body fields are absent.
  - inference rules match embedded adapter behavior:
    - `user` present => `main`
    - assistant-only history => `main`
    - tool/environment only => `side`
- Added regression tests in `AutoSkill4OpenClaw/tests/test_main_turn_proxy.py`:
  - missing explicit `turn_type` infers `main`
  - tool-only request infers `side`
  - inference helper behavior is pinned directly

### Validation
- Executed:
  - `python3 -m unittest AutoSkill4OpenClaw.tests.test_main_turn_proxy -q`
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q`
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `52/52` Python tests pass.
  - `54/54` adapter tests pass.

### Failed Attempts
- Initial attempt to compare `OpenClaw-RL` via GitHub web rendering was too noisy for code-level verification.
- Switched to a local shallow clone of `Gen-Verse/OpenClaw-RL` for direct source inspection.

### Self-Review Notes
- This is a low-risk parser-only change; no memory, provider, hook, or OpenClaw core behavior is modified.
- The fix matters because OpenClaw `2026.3.x` deployments may omit `turn_type`, which previously caused the sidecar proxy path to skip all main-turn extraction.

### Remaining Issues / Risks
- Embedded mode still depends on OpenClaw lifecycle hooks firing; it is not a drop-in replacement for RL-style proxy capture.
- `session_done` is still explicit-field-first; without it, the final pending main turn remains intentionally unextracted unless another close signal arrives.

### Next Step
- Decide whether embedded mode should remain the default recommendation when reliable RL-style sampling is required.

## 2026-03-13 - Round 1

### Scope
- Target area: `AutoSkill4OpenClaw/adapter` embedded runtime behavior consistency.
- Objective: make embedded runtime respect `openclawSkillInstallMode` (`openclaw_mirror` vs `store_only`) and verify with tests.

### Completed
- Baseline audit completed before coding:
  - Read core docs/config: `README.md`, `AutoSkill4OpenClaw/README.md`, `pyproject.toml`, `AutoSkill4OpenClaw/adapter/package.json`, plugin adapter source and tests.
  - Confirmed no root `Prompt.md` / `STATUS.md` existed.
  - Confirmed no CI workflow file in `.github/workflows/`.
- Implemented behavior fix in `AutoSkill4OpenClaw/adapter/embedded_runtime.js`:
  - Added `isMirrorInstallEnabled(cfg)`.
  - `skillInstallMode=store_only` now skips mirror copy to OpenClaw skills dir.
  - `skillInstallMode=openclaw_mirror` keeps existing mirror behavior.
  - Added structured result fields for observability when mirror is skipped:
    - `mirror_skipped: true`
    - `mirror_reason: "install_mode_store_only"`
- Added regression test in `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`:
  - `store_only` mode writes skill into AutoSkill SkillBank but does not mirror into OpenClaw skills dir.

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `24 passed, 0 failed`.

### Failed Attempts
- None in this round.

### Self-Review Notes
- Regression risk: low, change is gated by explicit install mode check.
- Backward compatibility:
  - default/unknown mode still behaves as mirror-enabled (`openclaw_mirror` semantics).
- Side effects:
  - no changes to `before_prompt_build`, memory hooks, provider hooks, or OpenClaw core paths.

### Remaining Issues / Risks
- Embedded mode env alias (`AUTOSKILL_OPENCLAW_NO_SIDECAR=1`) behavior is implemented but lacks explicit regression test.
- `embedded_runtime.js` and `embedded_runtime.test.mjs` are currently untracked files in git state and need final add/commit handling with related changes.
- Repository contains many unrelated modified files outside this scope; must avoid touching/reverting them.

### Next Step
- Round 2 (minimal increment):
  - Add config regression tests for no-sidecar env alias and install mode interplay.
  - Re-run adapter tests.
  - Update this `STATUS.md` with results.

## 2026-03-13 - Round 2

### Scope
- Target area: `AutoSkill4OpenClaw/adapter` config fallback correctness.
- Objective: lock down no-sidecar env alias behavior and prevent silent mode fallback mistakes.

### Completed
- Added config regression tests in `AutoSkill4OpenClaw/adapter/index.test.mjs`:
  - `AUTOSKILL_OPENCLAW_NO_SIDECAR=1` enables `runtimeMode=embedded` when runtime mode is otherwise unset.
  - Explicit `runtimeMode=sidecar` keeps sidecar mode even when no-sidecar alias is set.
- Fixed `normalizeConfig` in `AutoSkill4OpenClaw/adapter/index.js`:
  - Treat empty `AUTOSKILL_OPENCLAW_RUNTIME_MODE` as unset.
  - Prevent empty-string env from overriding `AUTOSKILL_OPENCLAW_NO_SIDECAR=1`.

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `26 passed, 0 failed`.

### Failed Attempts
- Initial test run failed (`25 passed, 1 failed`):
  - Failure: no-sidecar alias test expected `embedded` but got `sidecar`.
  - Root cause: `AUTOSKILL_OPENCLAW_RUNTIME_MODE=""` still participated in nullish-coalescing chain.
  - Resolution: normalize env runtime mode with trim and ignore empty string.

### Self-Review Notes
- Change is localized to config normalization logic; runtime behavior unchanged for explicit `runtimeMode`.
- Existing sidecar defaults remain intact.
- Added tests cover both positive and precedence path.

### Remaining Issues / Risks
- Adapter-related files `embedded_runtime.js` and `embedded_runtime.test.mjs` are still untracked in git state; needs explicit add/commit in integration step.
- Repository still contains many unrelated modified files; final merge should scope to plugin-specific paths only.

### Next Step
- Round 3 (integration finish line):
  - Final consistency pass on plugin docs vs config schema.
  - Optional: add one README note for `AUTOSKILL_OPENCLAW_NO_SIDECAR=1` alias.
  - Prepare scoped commit set for OpenClaw plugin paths only.

## 2026-03-13 - Round 3

### Scope
- Target area: plugin docs/config consistency.
- Objective: make no-sidecar alias behavior discoverable and consistent with implemented precedence.

### Completed
- Updated docs:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
- Added explicit mention:
  - `AUTOSKILL_OPENCLAW_NO_SIDECAR=1` as convenience alias.
  - precedence rule: explicit `runtimeMode` overrides alias.

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `26 passed, 0 failed`.

### Failed Attempts
- None in this round.

### Self-Review Notes
- Docs now match actual `normalizeConfig` precedence logic.
- No code-path changes in runtime behavior this round (documentation-only change + regression run).

### Remaining Issues / Risks
- Functional work for sidecar/embedded dual path is in place and validated at adapter test level.
- Remaining integration work is operational, not code correctness:
  - stage and commit only plugin-scoped files in a dirty worktree.
  - optional end-to-end validation in a real OpenClaw runtime environment.

### Completion Assessment
- Adapter-level feature target is **verifiably complete**:
  - no-sidecar embedded option available
  - BM25 maintenance retrieval in embedded path
  - session-closed extraction gating with successful `main` requirement
  - install mode semantics aligned (`store_only` no mirror, `openclaw_mirror` mirror)
  - regression tests passing
  - STATUS tracking in place

## 2026-03-13 - Round 4 (self-optimization)

### Scope
- Target area: embedded runtime + retrieval interaction.
- Objective: remove hidden default misbehavior where embedded mode could trigger sidecar-only retrieval calls.

### Issue Found (with evidence)
- In `normalizeConfig`, `store_only` previously auto-enabled `skillRetrieval`.
- In `runtimeMode=embedded` (no sidecar), `before_prompt_build` retrieval still tried calling sidecar hook endpoint.
- Impact:
  - unnecessary outbound calls and warning noise each turn
  - misleading runtime behavior in no-sidecar deployments

### Fix Applied
- In `AutoSkill4OpenClaw/adapter/index.js`:
  - added `autoDisableRetrievalByEmbeddedRuntime` default gate
  - `embedded` mode now disables retrieval by default unless explicitly enabled by config/env
  - added explicit disable reason: `embedded_runtime_mode`
  - improved log branch: `retrieval disabled by embedded runtime mode`
  - made `runtimeMode` empty string in config treated as unset (so no-sidecar alias still works)
- In docs:
  - updated embedded mode notes in `AutoSkill4OpenClaw/README.md` and `AutoSkill4OpenClaw/README.zh-CN.md` to state retrieval default-off in embedded mode.

### Test Coverage Added
- `AutoSkill4OpenClaw/adapter/index.test.mjs`:
  - embedded mode default disables retrieval
  - embedded mode explicit retrieval opt-in still works
  - empty `runtimeMode` config still honors no-sidecar alias
  - `before_prompt_build` in embedded default mode does not call external retrieval and logs expected disable reason

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
- Result:
  - `30 passed, 0 failed`.

### Failed Attempts
- None in this round.

### Self-Review Notes
- Risk/benefit:
  - high benefit: prevents silent per-turn misbehavior in no-sidecar default path
  - low risk: explicit retrieval opt-in remains available and tested
- Backward compatibility:
  - sidecar runtime defaults unchanged
  - openclaw_mirror retrieval-disable behavior unchanged

### Remaining Suggestions (not executed yet)
- Structural option: if product later requires `embedded + store_only + retrieval`, add local retrieval implementation in adapter (instead of sidecar HTTP hook dependency).
- Operational: final commit should include only plugin-scoped files due dirty worktree.

## 2026-03-13 - Round 5 (agent-trajectory robustness + prompt/path review)

### Scope
- Target area: agent trajectory ingestion robustness and OpenClaw skill artifact compatibility.
- Objective: reduce silent data loss during extraction/maintenance for tool-heavy agent sessions and improve generated SKILL.md safety.

### Issues Found (with evidence)
- Adapter dropped assistant turns when content was empty but `tool_calls` existed:
  - previous `normalizeMessages` only consumed `message.content`.
  - impact: tool-heavy trajectories could lose assistant evidence before `agent_end` extraction.
- Adapter mapped unknown roles to `user`, including `environment`:
  - impact: environment observations could be mislabeled as user intent.
- Embedded SKILL.md frontmatter did not sanitize newlines:
  - fields like `name/description/tags/triggers` could contain multiline LLM output and break frontmatter stability/parsing.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/index.js`
  - added assistant fallback serialization for `tool_calls/function_call/refusal/audio/annotations`.
  - mapped `environment` role to `tool` (instead of coercing to `user`).
  - added tool fallback content extraction from `result/output/observation`.
- `AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - added `oneLineYamlValue(...)` sanitizer.
  - frontmatter fields now force single-line safe values.
  - tags/triggers are normalized to one-line entries before rendering.

### Tests Added
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - `buildEndPayload preserves assistant tool-call messages and maps environment to tool`.
- `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`
  - `embedded runtime writes single-line frontmatter-safe metadata for generated SKILL.md`.

### Validation
- Executed:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - result: `32 passed, 0 failed`
- Prompt-profile sanity check:
  - `python3 AutoSkill4OpenClaw/tests/test_agentic_prompt_profile.py`
  - result: `Ran 4 tests, OK`
- Note:
  - `python3 -m pytest ...` unavailable in current environment (`No module named pytest`), so fallback used direct unittest script execution.

### Prompt/Profile Review Summary
- Sidecar path (`AutoSkill4OpenClaw/agentic_prompt_profile.py`) prompt set is relatively complete for agent trajectories:
  - extraction prompt includes evidence hierarchy, boundary/recency rules, de-identification, optional `scripts/references/assets`.
  - maintenance decision prompt has add/merge/discard policy with trajectory-specific guidance.
  - merge prompt enforces concise executable prompt + no examples metadata expansion.
- Embedded path (`AutoSkill4OpenClaw/adapter/embedded_runtime.js`) prompt set is currently much lighter:
  - works as minimal no-sidecar baseline.
  - lacks many sidecar-level guardrails (boundary detection, explicit provenance constraints, richer anti-oneoff criteria).

### Remaining Risks / Suggestions
- Structural (recorded, not executed in this round):
  - If embedded mode must match sidecar quality, either:
    - port a compact subset of `agentic_prompt_profile` rules into embedded prompts, or
    - expose a shared prompt profile package used by both Python and JS paths.
- OpenClaw integration operational checks:
  - ensure runtime/plugin config allows prompt augmentation when using `store_only` (`before_prompt_build` path).
  - in `openclaw_mirror` mode this is intentionally less critical since retrieval/invocation is delegated to OpenClaw native skill loading.

## 2026-03-13 - Round 6 (usage counters + safe pruning path)

### Scope
- Target area: OpenClaw plugin usage observability and stale-skill governance.
- Objective: add low-risk retrieval/usage counters (aligned with AutoSkill core counter model) without affecting OpenClaw main flow.

### Why this round
- User requirement: track skill retrieval/usage counts and support eventual stale-skill cleanup.
- Constraint: OpenClaw native `openclaw_mirror` retrieval/use path must remain untouched; tracking errors must never impact runtime behavior.

### Completed
- Added plugin-local usage tracker module:
  - `AutoSkill4OpenClaw/openclaw_usage_tracking.py`
  - best-effort counters via store `record_skill_usage_judgments` / `get_skill_usage_stats`
  - in-memory session retrieval cache with TTL/size limits
  - default-safe pruning OFF (`prune_enabled=false`)
- Integrated tracker into OpenClaw service runtime:
  - `AutoSkill4OpenClaw/service_runtime.py`
  - `before_agent_start` remembers retrieval snapshots by `user_id + session_id`
  - `agent_end` records counters using explicit retrieval payload (preferred) or cached snapshot fallback
  - extraction chain remains unchanged; usage-tracking failures are swallowed/logged
  - when usage-based prune deletes skills, mirror sync is triggered (if mirror mode enabled)
  - added API endpoint:
    - `POST /v1/autoskill/openclaw/usage/stats`
  - exposed in capabilities/openapi
- Added adapter-side pass-through for usage signals:
  - `AutoSkill4OpenClaw/adapter/index.js`
  - caches retrieval snapshot from `before_prompt_build` response per session
  - forwards retrieval snapshot on `agent_end` payload
  - forwards explicit `used_skill_ids` when present in event/context payload
  - all logic is additive and does not modify messages/system prompt replacement behavior
- Added runtime/config/env wiring:
  - `AutoSkill4OpenClaw/run_proxy.py`
  - `AutoSkill4OpenClaw/install.py`
  - new env knobs:
    - `AUTOSKILL_OPENCLAW_USAGE_TRACKING_ENABLED`
    - `AUTOSKILL_OPENCLAW_USAGE_PRUNE_ENABLED`
    - `AUTOSKILL_OPENCLAW_USAGE_PRUNE_MIN_RETRIEVED`
    - `AUTOSKILL_OPENCLAW_USAGE_PRUNE_MAX_USED`
    - `AUTOSKILL_OPENCLAW_USAGE_MAX_HITS_PER_TURN`
    - `AUTOSKILL_OPENCLAW_USAGE_MAX_PENDING_SESSIONS`
    - `AUTOSKILL_OPENCLAW_USAGE_PENDING_TTL_S`
- Documentation updated:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
  - added “Skill Usage Counters / 技能使用计数” section with safe defaults and stats endpoint.

### Validation
- JS adapter tests:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - result: `33 passed, 0 failed`
- Python plugin tests:
  - `python3 AutoSkill4OpenClaw/tests/test_usage_tracking.py`
  - `python3 AutoSkill4OpenClaw/tests/test_service_runtime.py`
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'`
  - result: all passing (`33` plugin Python tests total)

### Tests added/updated
- Added:
  - `AutoSkill4OpenClaw/tests/test_usage_tracking.py`
- Updated:
  - `AutoSkill4OpenClaw/tests/test_service_runtime.py`
  - `AutoSkill4OpenClaw/adapter/index.test.mjs`

### Risk assessment
- Low runtime risk:
  - usage tracking is best-effort and isolated from extraction/main request success path.
  - defaults keep auto-prune disabled.
- Known limitation:
  - in `openclaw_mirror` mode, if OpenClaw does not emit explicit used-skill signals, `used` counts are sparse.
  - retrieval counters are strongest in `store_only` + `before_prompt_build` path where retrieval snapshots are observable.

### Next optimization candidates
- Add optional “mirror-mode estimation” strategy (disabled by default) to infer usage from session replay + retrieval replay, with conservative confidence gating.
- Add lightweight usage trend endpoint (top retrieved / never used / recently used) for ops dashboards.

## 2026-03-13 - Round 7 (prune safety hardening + re-validation)

### Scope
- Target area: usage-based auto-pruning safety.
- Objective: prevent accidental skill pruning when runtime does not provide explicit used-skill signals.

### Issue Found
- Even with conservative defaults, if users manually enable prune in environments that do not reliably emit `used_skill_ids`, stale-skill pruning can become over-aggressive.

### Fix Applied
- Added hard safety gate in usage tracker:
  - `prune_require_explicit_used_signal` (default `true`).
  - when enabled, prune thresholds are suppressed (`0`) unless current payload includes explicit `used_skill_ids`.
- Wiring updates:
  - `AutoSkill4OpenClaw/openclaw_usage_tracking.py`
  - `AutoSkill4OpenClaw/run_proxy.py`
  - `AutoSkill4OpenClaw/install.py`
- Docs updated (EN/ZH) with explicit safety behavior and env var:
  - `AUTOSKILL_OPENCLAW_USAGE_PRUNE_REQUIRE_EXPLICIT_USED_SIGNAL=1`

### Tests Added/Updated
- `AutoSkill4OpenClaw/tests/test_usage_tracking.py`
  - added prune gate regression (no used signal => prune disabled; with signal => prune enabled).
- `AutoSkill4OpenClaw/tests/test_run_proxy_defaults.py`
  - added default assertion for `openclaw_usage_prune_require_explicit_used_signal=1`.

### Validation
- `python3 AutoSkill4OpenClaw/tests/test_usage_tracking.py` (pass)
- `python3 AutoSkill4OpenClaw/tests/test_run_proxy_defaults.py` (pass)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'` (pass, 34 tests)
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 33 tests)

### Residual Risks
- In strict `openclaw_mirror` black-box usage flow, `used` counters still depend on upstream signal availability.
- This round intentionally favors false-negatives (do not prune) over false-positives (wrong prune), to keep runtime safety first.

## 2026-03-13 - Round 8 (streaming header correctness + cache isolation hardening)

### Scope
- Target area:
  - main-turn proxy stream forwarding robustness
  - adapter retrieval cache session isolation
- Objective:
  - prevent malformed stream response headers
  - avoid cross-user retrieval snapshot contamination when `session_id` collides

### Issues Found
- `openclaw_main_turn_proxy._copy_headers_to_client` could emit `Content-Length: 0` for stream forwarding when upstream carried `Content-Length`.
  - Risk: some clients may prematurely treat stream body as empty.
- Adapter retrieval cache keyed only by `session_id`.
  - Risk: multi-user deployments with same `session_id` can mix retrieval snapshots, affecting usage accounting quality.

### Fixes Applied
- `AutoSkill4OpenClaw/openclaw_main_turn_proxy.py`
  - stream/header fix: do not synthesize `Content-Length: 0` when `content_length` is unknown (`None`).
  - keep explicit `Content-Length` only for non-stream path where body size is known.
- `AutoSkill4OpenClaw/adapter/index.js`
  - retrieval cache key changed to `user_id + session_id` (case-normalized).
  - threaded user key through `onRetrieval / consumeRetrieval / clearRetrieval` flow.
  - backward compatibility preserved for paths that do not provide user id.

### Tests Added/Updated
- `AutoSkill4OpenClaw/tests/test_main_turn_proxy.py`
  - added regression: stream response header copy must not contain forced `content-length`.
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - added retrieval cache isolation test (`same session_id`, different users).
  - added backward compatibility test for missing user id cache flow.

### Validation
- Python:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'`
  - result: `35 passed, 0 failed`
- Adapter:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - result: `35 passed, 0 failed`

### Residual Risks / Next Candidates
- Main-turn proxy currently logs extensively in tests/runtime; consider adding opt-in structured log levels if noise becomes operationally expensive.
- End-to-end live OpenClaw runtime verification (real gateway + real model stream edge cases) is still recommended before production rollout.

## 2026-03-13 - Round 9 (hard dedupe + session timeout closure + verification scripts)

### Scope
- Target area:
  - cross-trigger extraction dedupe (`main-turn` vs `agent_end`)
  - optional session idle-timeout closure for `agent_end` fallback extraction
  - runnable acceptance scripts for sidecar/embedded paths
- Objective:
  - reduce duplicate extraction/maintenance updates under mixed trigger configs
  - close stale sessions safely when `session_done` is missing
  - provide repeatable validation entrypoints for operators

### Issues Addressed
- Duplicate extraction risk remained when users explicitly enabled both:
  - `AUTOSKILL_OPENCLAW_MAIN_TURN_EXTRACT=1`
  - `AUTOSKILL_OPENCLAW_AGENT_END_EXTRACT=1`
- Session close fallback previously depended only on:
  - `session_done=true` or
  - `session_id` change
  - which can delay extraction if callers omit explicit close signal.

### Fixes Applied
- `AutoSkill4OpenClaw/service_runtime.py`
  - added hard dedupe check:
    - `agent_end` session-close fallback now skips sessions that already have non-failed `openclaw_main_turn_proxy` extraction events.
  - added window-level dedupe registry for OpenClaw extraction scheduling:
    - builds/uses `dedupe_key` for `openclaw_main_turn_proxy` and `openclaw_agent_end_session_end`.
    - duplicate windows emit `status=skipped` extraction events instead of running duplicate jobs.
  - integrated archive idle sweep before `append_session_record`:
    - stale active sessions can be closed and extracted on next hook arrival.
- `AutoSkill4OpenClaw/openclaw_conversation_archive.py`
  - added config:
    - `session_idle_timeout_seconds` (default `0`, disabled)
  - tracks active-session touch timestamps.
  - added `sweep_inactive_sessions(user_id=...)` API.
  - keeps ended-session outputs deduplicated.
- config/install wiring:
  - `AutoSkill4OpenClaw/run_proxy.py`
    - new CLI/env:
      - `--openclaw-session-idle-timeout-s`
      - `AUTOSKILL_OPENCLAW_SESSION_IDLE_TIMEOUT_S`
  - `AutoSkill4OpenClaw/install.py`
    - writes `AUTOSKILL_OPENCLAW_SESSION_IDLE_TIMEOUT_S=0` into generated `.env`.
- verification scripts added:
  - `AutoSkill4OpenClaw/scripts/verify_sidecar.sh`
  - `AutoSkill4OpenClaw/scripts/verify_embedded.sh`
- docs updated:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`

### Tests Added/Updated
- added:
  - `AutoSkill4OpenClaw/tests/test_conversation_archive.py`
    - idle-timeout disabled no-op
    - idle-timeout closes active session
- updated:
  - `AutoSkill4OpenClaw/tests/test_service_runtime.py`
    - agent_end dedupe skip when main-turn extraction already exists
    - idle-timeout closure triggers session-end extraction scheduling
    - window-level dedupe skips duplicate scheduling
  - `AutoSkill4OpenClaw/tests/test_run_proxy_defaults.py`
    - default assertion for `openclaw_session_idle_timeout_s == 0`

### Validation
- Python tests:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'`
  - result: `40 passed, 0 failed`
- Adapter tests:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - result: `35 passed, 0 failed`
- Embedded verification script:
  - `bash AutoSkill4OpenClaw/scripts/verify_embedded.sh`
  - result: pass (embedded + adapter test flows)

### Failed Attempts / Corrections
- Initial idle-timeout archive test used touch timestamp `0`, which is treated as invalid/no-touch by implementation.
- Corrected tests to use a minimal positive stale timestamp (`1`) and strengthened runtime timeout path assertion.

### Residual Risks / Next Candidates
- Sidecar verification script requires a running local sidecar service and real endpoint reachability; not executed in this round.
- If operators use very short idle-timeout values, sessions may be closed too aggressively in bursty workloads; recommended to keep timeout disabled (`0`) unless explicitly needed.

## 2026-03-13 - Round 10 (embedded invocation multi-fallback chain)

### Scope
- Target area: `AutoSkill4OpenClaw/adapter` embedded extraction/maintenance model invocation.
- Objective: when runtime reflection cannot call model successfully, add full fallback chain:
  - `openclaw-runtime` (direct invoke + runtime target resolve)
  - `openclaw-runtime-subagent`
  - `openclaw-config-resolve`
  - `manual`

### Why this round
- User required a no-sidecar embedded path that does not depend on manual model config by default, but still has deterministic fallback behavior when runtime APIs are not available.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - replaced single-path runtime invoke with multi-mode invocation chain.
  - added `openclaw-runtime` dual behavior:
    - try runtime direct model invoker functions first
    - if failed, resolve `base_url/api_key/model` from runtime object and call OpenAI-compatible chat endpoint.
  - added `openclaw-runtime-subagent` mode:
    - probes runtime subagent/internal reasoning methods (`runSubAgent` / `invokeSubAgent` / etc.).
  - added `openclaw-config-resolve` mode:
    - reads OpenClaw config candidates (`openclaw.json`, `models.json`, agent-level models) and resolves provider/model/base_url/api_key (including env references).
  - added `manual` mode:
    - explicit fallback for manual `base_url/api_key/model`.
  - HTTP-call path supports timeout/retry and remains fail-open (errors become extraction job failures, never block main conversation).
  - preserved recursion safety (`autoskill_internal` + internal depth guard) and session-close gating.
- `AutoSkill4OpenClaw/adapter/index.js`
  - added embedded invocation config normalization with env support:
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_MODES`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_TIMEOUT_MS`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_RETRIES`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_OPENCLAW_HOME`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_BASE_URL`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_API_KEY`
    - `AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_MODEL`
  - default invocation order set to:
    - `openclaw-runtime,openclaw-runtime-subagent,openclaw-config-resolve,manual`
- `AutoSkill4OpenClaw/adapter/openclaw.plugin.json`
  - added config schema for `embedded.modelInvocation`.
- docs updated:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
  - embedded section now documents fallback order and new env knobs.

### Tests Added/Updated
- `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`
  - runtime direct failure -> runtime-target HTTP fallback.
  - runtime unavailable -> config-resolve fallback.
  - runtime+config unavailable -> manual fallback.
  - runtime subagent mode success path.
  - all modes fail -> fail-open result (`session_not_extractable` + per-session failed job).
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - config normalization default mode order assertion.
  - env overrides for embedded invocation modes/timeouts/retries/openclawHome/manual params.

### Validation
- Adapter:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - result: `41 passed, 0 failed`
- Plugin Python tests:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'`
  - result: `40 passed, 0 failed`
- Syntax:
  - `node --check AutoSkill4OpenClaw/adapter/index.js`
  - `node --check AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - result: pass

### Failed Attempts / Corrections
- New embedded fallback tests initially failed due test helper shallow-merge behavior that dropped `embedded.sessionArchiveDir`.
- Corrected `makeConfig` in `embedded_runtime.test.mjs` to deep-merge embedded overrides.

### Residual Risks / Next Candidates
- `openclaw-config-resolve` is best-effort for heterogeneous OpenClaw configs; secret-ref/OAuth-only keys may remain unresolved and correctly fall through to next mode.
- Runtime object introspection is intentionally conservative to avoid hard-coupling to internal unstable APIs; if specific OpenClaw versions expose additional official runtime APIs, probe list can be extended with low risk.

## 2026-03-13 - Round 11 (subagent maintenance and merge hardening)

### Scope
- Target area: embedded `openclaw-runtime-subagent` path after candidate extraction.
- Objective: harden maintenance decision and merge behavior (not extraction-only), preventing unsafe merge and duplicate skill bloat.

### Issues Found
- Maintenance merge in embedded path could be overly permissive:
  - LLM `merge` decision with weak/invalid target could still drift toward wrong merge.
- Candidate parsing robustness gap:
  - subagent outputs may return `skill` object or direct object, not always `skills[]`.
- No deterministic duplicate guard before maintenance:
  - exact duplicate candidate could still enter decision pipeline and produce redundant skill files.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - added skill payload normalization:
    - clamps (`name/description/prompt`) and dedupes triggers/tags.
    - extraction now accepts `skills[]`, `skill`, or direct object shape.
  - strengthened maintenance decision policy:
    - action normalization supports common synonyms.
    - merge requires valid explicit target id or high-confidence BM25 fallback (`score >= 0.72`).
    - unsafe merge now degrades to `add`.
  - removed blind `hits[0]` merge fallback in `maintainSkill`; merge now requires resolved valid target.
  - added deterministic duplicate guard before decision:
    - if candidate matches existing skill (prompt equality / strong normalized overlap), skip with `duplicate_existing_skill`.
  - retained fail-open behavior and recursion guard.
- docs updated (EN/ZH) to include embedded maintenance safety guards.

### Tests Added
- `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`
  - explicit merge target in subagent mode -> merged + version bump.
  - invalid/unsafe merge target -> fall back to add.
  - duplicate candidate -> skipped before maintenance call.

### Validation
- Adapter:
  - `cd AutoSkill4OpenClaw/adapter && npm test`
  - result: `44 passed, 0 failed`
- Plugin Python tests:
  - `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'`
  - result: `40 passed, 0 failed`

### Residual Risks / Next Candidates
- Current duplicate guard is conservative lexical matching; semantic near-duplicates still rely on BM25+LLM maintenance decision.
- If production data shows false merge/add boundaries, threshold (`0.72`) can be moved to config in a later low-risk round.

## 2026-03-13 - Round 12 (README mainline switch to no-sidecar embedded)

### Scope
- Target area: `AutoSkill4OpenClaw/README.md` and `AutoSkill4OpenClaw/README.zh-CN.md`.
- Objective: make no-sidecar embedded runtime the primary user-facing mainline, with sidecar repositioned as optional.

### Changes
- Rewrote top-level positioning in EN/ZH docs:
  - mainline is now `runtimeMode=embedded` (no sidecar required).
  - sidecar moved to optional runtime/control-plane role.
- Reworked Quick Start in EN/ZH:
  - now starts from editing `~/.openclaw/openclaw.json` plugin config for embedded mode.
  - removed sidecar startup as mandatory step.
  - added local verification steps for SkillBank + OpenClaw mirrored skills.
- Reframed path sections:
  - default path diagrams/wording now describe embedded `agent_end` processing.
  - sidecar interaction moved under explicitly optional section.
- Updated env var grouping:
  - recommended path now lists embedded-oriented keys.
  - sidecar-only operations/endpoints are explicitly labeled.
- Clarified local storage paths for embedded vs sidecar archives.

### Validation
- Documentation consistency check by manual scan of EN/ZH files.
- No code-path changes in this round; runtime behavior unchanged.

### Residual Notes
- Runtime default in code remains backward-compatible (`sidecar`) unless explicitly configured to embedded; docs now instruct explicit embedded config for new deployments.

## 2026-03-13 - Round 13 (usage counting hybrid fallback: explicit + inferred)

### Scope
- Target area: OpenClaw plugin usage observability (`adapter -> service_runtime -> openclaw_usage_tracking`).
- Objective: improve count coverage in native OpenClaw skill flow while keeping prune safety unchanged.

### Issues Found
- Existing counting was explicit-signal heavy:
  - `used` could not be counted when runtime omitted `used_skill_ids`.
  - no retrieval snapshot + no explicit signal meant full skip (`no_retrieval_hits`).
- Prune safety requirement remained strict:
  - never let inferred signals drive auto-prune.

### Fixes Applied
- `AutoSkill4OpenClaw/openclaw_usage_tracking.py`
  - added hybrid counting model:
    - `skills_explicit` (store-backed strict counters, prune source)
    - `skills_inferred` (plugin-local inferred counters, persisted JSON)
    - `skills_combined` (observability aggregate only)
  - added synthetic fallback snapshot path:
    - if retrieval hits are missing but explicit/inferred used ids exist, build synthetic hits and still count.
  - added inferred signal resolver:
    - payload inferred ids
    - selected-for-use/context ids
    - optional assistant/tool message mention matching
  - prune remains explicit-only and still guarded by `AUTOSKILL_OPENCLAW_USAGE_PRUNE_REQUIRE_EXPLICIT_USED_SIGNAL=1`.
- `AutoSkill4OpenClaw/service_runtime.py`
  - extracts and forwards `inferred_used_skill_ids`.
  - passes message window to usage tracker for mention-based inference.
  - logs inference status in usage tracking line.
- `AutoSkill4OpenClaw/adapter/index.js`
  - adds best-effort collection of `inferred_used_skill_ids` from event/ctx/retrieval.
  - forwards inferred ids on `agent_end` payload when explicit ids are absent.
- Config wiring:
  - `AutoSkill4OpenClaw/run_proxy.py`
    - `AUTOSKILL_OPENCLAW_USAGE_INFER_ENABLED`
    - `AUTOSKILL_OPENCLAW_USAGE_INFER_FROM_SELECTED_IDS`
    - `AUTOSKILL_OPENCLAW_USAGE_INFER_FROM_MESSAGE_MENTIONS`
    - `AUTOSKILL_OPENCLAW_USAGE_INFER_MAX_MESSAGE_CHARS`
    - `AUTOSKILL_OPENCLAW_USAGE_INFER_MANIFEST_PATH`
  - `AutoSkill4OpenClaw/install.py` writes default env entries for the new knobs.

### Tests Added/Updated
- Python:
  - `AutoSkill4OpenClaw/tests/test_usage_tracking.py`
    - explicit-used fallback without retrieval hits
    - inferred counting when explicit used is absent
    - inference skip when explicit used is present
  - `AutoSkill4OpenClaw/tests/test_service_runtime.py`
    - inferred fallback end-to-end through `agent_end` and stats endpoint
  - `AutoSkill4OpenClaw/tests/test_run_proxy_defaults.py`
    - default assertions for new usage inference flags
- JS:
  - `AutoSkill4OpenClaw/adapter/index.test.mjs`
    - verifies `agent_end` forwards `inferred_used_skill_ids` when explicit signal is absent

### Validation
- `python3 AutoSkill4OpenClaw/tests/test_usage_tracking.py` (pass)
- `python3 AutoSkill4OpenClaw/tests/test_service_runtime.py` (pass)
- `python3 AutoSkill4OpenClaw/tests/test_run_proxy_defaults.py` (pass)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'` (pass, 44 tests)
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 45 tests)

### Risk / Safety Notes
- Inferred counters are additive observability only; pruning still reads strict explicit counters.
- Main dialog/extraction path remains fail-open:
  - usage tracking errors are swallowed and only logged.

## 2026-03-13 - Round 14 (shared prompt pack for sidecar + embedded)

### Scope
- Target area: prompt consistency between sidecar prompt profile and embedded runtime.
- Objective: eliminate prompt drift by introducing one shared prompt source used by both paths.

### Issues Found
- Prompt definitions were split across:
  - `AutoSkill4OpenClaw/agentic_prompt_profile.py` (sidecar)
  - `AutoSkill4OpenClaw/adapter/embedded_runtime.js` (embedded)
- This created high drift risk when updating extraction / maintenance / merge policies.

### Fixes Applied
- Added shared prompt pack:
  - `AutoSkill4OpenClaw/adapter/openclaw_prompt_pack.txt`
  - includes reusable shared blocks plus sidecar/embedded templates:
    - `sidecar.extract.system`
    - `sidecar.extract.repair.system`
    - `sidecar.maintain.decide.system`
    - `sidecar.maintain.merge.system`
    - `embedded.extract.system`
    - `embedded.maintain.decide.system`
    - `embedded.maintain.merge.system`
- Added Python loader/renderer:
  - `AutoSkill4OpenClaw/openclaw_prompt_pack.py`
  - supports `{{block.*}}` and `{{var.*}}` template rendering
  - supports override path via `AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH`
  - fail-open fallback to built-in prompts when file is missing/invalid
- Wired sidecar prompt profile to shared templates:
  - `AutoSkill4OpenClaw/agentic_prompt_profile.py`
  - extraction, repair, maintenance decision, and merge prompts now render from shared pack first, then fallback to legacy inline prompt text.
- Wired embedded runtime to shared templates:
  - `AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - extraction/maintenance/merge system prompts now render from shared pack first, then fallback to legacy inline prompt text.
  - added embedded runtime logs for prompt-pack loaded/fallback path.

### Tests Added/Updated
- New Python tests:
  - `AutoSkill4OpenClaw/tests/test_openclaw_prompt_pack.py`
    - default pack loads with version
    - sidecar + embedded extract prompts both include shared block marker
    - template fallback behavior
    - custom pack block/var rendering
- Updated JS tests:
  - `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`
    - verifies embedded runtime reads custom prompt pack templates and renders block/variable substitutions.

### Validation
- `python3 -m unittest AutoSkill4OpenClaw/tests/test_openclaw_prompt_pack.py` (pass)
- `python3 AutoSkill4OpenClaw/tests/test_agentic_prompt_profile.py` (pass)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'` (pass, 48 tests)
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 46 tests)

### Documentation
- Updated:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
- Added section explaining shared prompt pack path, override env, and fail-open fallback.

### Risk / Safety Notes
- Runtime behavior remains fail-open:
  - if shared prompt pack is unavailable or malformed, both runtimes automatically fallback to built-in prompts.
- No changes to OpenClaw memory slots / contextEngine / compaction / tools / provider routing.

## 2026-03-13 - Round 15 (prompt-pack config ergonomics + integration coverage)

### Scope
- Target area: shared prompt-pack operability and regression coverage.
- Objective: ensure prompt-pack path override works from standard plugin config (not env-only), and verify sidecar prompt-profile actually consumes the shared pack.

### Issues Found
- Embedded prompt-pack override was effectively env-driven:
  - `embedded_runtime.js` accepted `cfg.embedded.promptPackPath`, but `normalizeConfig` did not preserve this field.
- Sidecar tests validated prompt text content but did not explicitly prove that `AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH` can override prompt source end-to-end in prompt-profile builders.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/index.js`
  - Added `embedded.promptPackPath` to normalized config output.
  - Added default field in `DEFAULTS.embedded`.
  - Supports both plugin config and env override:
    - config: `plugins.entries.autoskill-openclaw-adapter.config.embedded.promptPackPath`
    - env: `AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH`
- `AutoSkill4OpenClaw/install.py`
  - Added `AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH=` to generated `.env` template.
- `AutoSkill4OpenClaw/tests/test_agentic_prompt_profile.py`
  - Added integration-style test proving sidecar extract prompt can be overridden via shared prompt pack env path.
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - Added config normalization tests for prompt-pack override via config/env.
- Docs updated:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
  - now include both env and plugin-config override examples.

### Validation
- `python3 AutoSkill4OpenClaw/tests/test_agentic_prompt_profile.py` (pass, 5 tests)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'` (pass, 49 tests)
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 48 tests)

### Residual Suggestions
- Parser/runtime consistency still uses two lightweight implementations (Python + JS) over one shared pack format.
- Current risk is low and covered by tests, but future work can factor a tiny formal schema test corpus (golden render cases) consumed by both test suites to further reduce parser drift risk.

## 2026-03-13 - Round 16 (embedded live session snapshot persistence)

### Scope
- Target area: embedded session archival behavior.
- Objective: persist session data locally in real time per incoming turn (without waiting for session end), while keeping extraction trigger at session close.

### Changes Applied
- `AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - Added live snapshot writer:
    - active snapshot path: `<session>.latest.json` under `embedded.sessionArchiveDir/<user>/`
    - updated on every `handle(payload, ...)` call after appending JSONL event row
  - Added in-memory rolling state (`liveSessionByKey`) to avoid expensive full-file rescans for each live snapshot update.
  - Added snapshot finalization on session close/session switch:
    - renames `.latest.json` to timestamped closed file, aligned with JSONL close semantics.
  - Extended non-closed return payload with `session_snapshot_path` for observability.
- Existing extraction behavior remains unchanged:
  - extraction still runs only on closed sessions with successful `turn_type=main` evidence.

### Tests Added
- `AutoSkill4OpenClaw/adapter/embedded_runtime.test.mjs`
  - `embedded runtime persists live session snapshot before session end`
  - verifies:
    - no extraction call before session close
    - `.latest.json` exists and updates turn_count/messages incrementally
    - `session_snapshot_path` is returned in no-end response

### Documentation
- Updated storage section:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
  - now includes embedded live snapshot path.

### Validation
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'` (pass)

### Risk Notes
- Write frequency increases in embedded mode (one extra small JSON write per turn). This is intentional for real-time local visibility.
- Fail-open behavior unchanged; extraction/memory/tool/provider paths are not coupled to snapshot write success logic.

## 2026-03-13 - Round 17 (embedded live-stage from before_prompt_build)

### Scope
- Target area: environments where `agent_end` hook cadence is insufficient for real-time session visibility.
- Objective: ensure embedded session files are staged during active chat turns, not only through `agent_end`.

### Issue Found
- Although embedded runtime now supports per-turn snapshot writes, writes were still triggered from `agent_end` path.
- In some deployments, `agent_end` is sparse or payload shape differs, so users may not see files updating while chatting.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/embedded_runtime.js`
  - exposed `stageLive(payload, event, ctx)`:
    - stages JSONL + `.latest.json` snapshot only
    - does not trigger extraction/maintenance jobs
- `AutoSkill4OpenClaw/adapter/index.js`
  - `before_prompt_build` now calls embedded `stageLive(...)` (best-effort, fail-open) when runtime is embedded.
  - this path runs before retrieval checks, so it still stages local session snapshots when retrieval is disabled.
  - added `buildEmbeddedLivePayload(...)` helper to construct lightweight staging payload from current hook context.
  - wired `embeddedProcessor` into `before_prompt_build` handler registration.

### Tests Added/Updated
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - added `before_prompt_build stages embedded live session snapshot even when retrieval is disabled`.
- Existing embedded runtime live snapshot tests remain green.

### Validation
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 50 tests)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -p 'test_*.py'` (pass, 49 tests)

### Risk Notes
- Added one lightweight local-write path on `before_prompt_build`; failures are swallowed and logged, never blocking prompt flow.
- Extraction triggering behavior remains in `agent_end` path; `stageLive` intentionally avoids model calls.

## 2026-03-13 - Round 18 (OpenClaw 2026.3.x turn field compatibility fallback)

### Scope
- Target area: adapter hook payload compatibility when OpenClaw runtime does not expose `turn_type/session_done` in `event/ctx`.
- Objective: avoid false `no_successful_main_turn` skips caused by missing `turn_type` fields in some OpenClaw 2026.3.x builds.

### Issue Found
- Adapter previously treated missing `turn_type` as empty.
- Downstream extraction gates require at least one successful `turn_type=main` in a closed session.
- Result: when runtime omitted turn fields, valid sessions could be archived but skipped for extraction.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/index.js`
  - added `inferTurnTypeByMessages(...)` fallback:
    - if any `user` message exists -> infer `main`
    - if assistant-only (without tool-only trace) -> infer `main`
    - if only tool/environment messages -> infer `side`
  - explicit `turnType/turn_type` still has highest priority.
  - wired fallback for both:
    - embedded live-stage payload (`before_prompt_build`)
    - `agent_end` payload construction
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - added regression tests:
    - infers `main` when runtime omits turn fields
    - infers `side` for tool/environment-only records

### Documentation
- Updated:
  - `AutoSkill4OpenClaw/README.md`
  - `AutoSkill4OpenClaw/README.zh-CN.md`
- Added explicit compatibility notes for:
  - missing `turn_type` inference behavior
  - missing `session_done` fallback behavior (`session_id` boundary / sidecar idle-timeout close)

### Validation
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 52 tests)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q` (pass, 49 tests)

### Risk Notes
- This is a compatibility fallback, not a protocol replacement.
- If your deployment can provide explicit `turn_type`, explicit values always override inferred values.

## 2026-03-13 - Round 19 (hook alias compatibility for OpenClaw lifecycle naming drift)

### Scope
- Target area: adapter hook registration compatibility in OpenClaw environments where lifecycle hook names may differ by naming style.
- Objective: avoid "plugin loaded but hooks never trigger" in deployments that expose camelCase hook names.

### Issue Found
- Field reports showed adapter startup logs present (plugin loaded), but no per-turn hook logs and no embedded session writes.
- This pattern indicates hook name mismatch risk across versions (`before_prompt_build`/`agent_end` vs camelCase variants).

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/index.js`
  - introduced hook alias registration sets:
    - `before_prompt_build`, `beforePromptBuild`
    - `agent_end`, `agentEnd`
  - added `registerLifecycleHooks(...)` helper:
    - registers all aliases
    - logs successful registration names
    - fail-open per alias, fail-hard only when all aliases fail
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - updated registration test to assert both snake_case and camelCase aliases are registered.
  - preserved guard that `before_agent_start` is not reintroduced.

### Validation
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 52 tests)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q` (pass, 49 tests)

### Risk Notes
- Registering aliases may cause duplicate callbacks only if a runtime emits both naming variants for the same turn.
- Existing extraction dedupe and fail-open behavior remain intact; no OpenClaw core patching introduced.

## 2026-03-13 - Round 20 (typed hook registration correctness for OpenClaw 2026.3.x)

### Scope
- Target area: lifecycle hook wiring in adapter register path.
- Objective: fix the real trigger blocker where plugin is loaded but typed lifecycle hooks are never fired.

### Issue Found
- Adapter previously preferred `api.registerHook(...)` when both `registerHook` and `on` existed.
- In OpenClaw 2026.3.x, typed lifecycle hooks (`before_prompt_build`, `agent_end`) are registered through `api.on(...)`, while `registerHook` is for internal hooks.
- Result: plugin can appear loaded (prompt pack log present), but per-turn lifecycle callbacks are not triggered.

### Fixes Applied
- `AutoSkill4OpenClaw/adapter/index.js`
  - changed hook registration priority:
    - prefer `api.on(...)` first
    - fallback to `api.registerHook(...)` only if `on` is unavailable
  - removed non-official camelCase hook alias registration; keep official typed names only:
    - `before_prompt_build`
    - `agent_end`
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - restored registration assertion to official snake_case hook names.
  - added regression test:
    - when both `on` and `registerHook` exist, adapter must register typed lifecycle hooks via `on`.

### Validation
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 53 tests)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q` (pass, 49 tests)

### Risk Notes
- Very low risk: this aligns adapter behavior to OpenClaw official typed lifecycle API.
- Backward compatibility preserved for environments exposing only `registerHook` (fallback path retained).

## 2026-03-14 - Round 21 (runtime hook diagnostics logging)

### Scope
- Target area: production troubleshooting for "hooks registered but never invoked".
- Objective: provide explicit logs to distinguish registration success from runtime callback execution.

### Changes Applied
- `AutoSkill4OpenClaw/adapter/index.js`
  - hook registration logs now include binding method:
    - `method=on` or `method=registerHook`
  - plugin startup logs hook API capability snapshot:
    - `has_api_on`, `has_registerHook`, `runtime_mode`
  - added first-invocation diagnostics:
    - `hook first invocation name=before_prompt_build`
    - `hook first invocation name=agent_end`
  - added one-shot watchdog warning after startup (60s):
    - emits if either lifecycle hook still has zero invocations
    - helps confirm "plugin loaded but traffic not entering agent lifecycle"
- `AutoSkill4OpenClaw/adapter/index.test.mjs`
  - added regression case asserting first-invocation diagnostics are logged.

### Validation
- `cd AutoSkill4OpenClaw/adapter && npm test` (pass, 54 tests)
- `python3 -m unittest discover -s AutoSkill4OpenClaw/tests -q` (pass, 49 tests)

### Risk Notes
- Diagnostics are low-risk and fail-open.
- Watchdog uses `setTimeout(...).unref()` to avoid holding process lifecycle.
