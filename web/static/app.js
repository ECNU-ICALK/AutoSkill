/* global fetch */

const state = {
  sessionId: null,
  messages: [],
  lastResult: null,
  inFlight: false,
  savingSkill: false,
  deletingSkill: false,
  rollingBackSkill: false,
  editingSkillId: null,
  skillEditorDirty: false,
  pollTimer: null,
  extractionJobId: null,
  extractionStatus: "",
  extractionStartedAtMs: null,
  extractionFinishedAtMs: null,
  extractionRunningTimer: null,
  extractionElapsedTimer: null,
  retrievalPulseTimer: null,
  turnSeq: 0,
  turnById: Object.create(null),
  jobTurnMap: Object.create(null),
  trace: {
    sessionStartedAt: Date.now(),
    turns: [],
    retrievalEvents: [],
    extractionEvents: [],
    configEvents: [],
  },
};

function el(id) {
  return document.getElementById(id);
}

function cloneJsonSafe(v) {
  try {
    return JSON.parse(JSON.stringify(v == null ? null : v));
  } catch (_e) {
    return null;
  }
}

function setStatus(ok, text) {
  const badge = el("statusBadge");
  badge.textContent = text;
  badge.className = ok ? "badge badge--ok" : "badge badge--err";
}

function newTurn(text) {
  state.turnSeq += 1;
  const id = `turn_${state.turnSeq}`;
  const turn = {
    id,
    input: String(text || ""),
    startedAt: Date.now(),
    finishedAt: null,
    kind: "unknown",
    command: "",
    chatAppend: [],
    retrieval: null,
    extraction: null,
    error: "",
  };
  state.turnById[id] = turn;
  state.trace.turns.push(turn);
  return turn;
}

function getTurn(turnId) {
  if (!turnId) return null;
  return state.turnById[String(turnId)] || null;
}

function finishTurn(turnId, patch) {
  const turn = getTurn(turnId);
  if (!turn) return;
  if (patch && typeof patch === "object") {
    Object.assign(turn, patch);
  }
  if (!turn.finishedAt) turn.finishedAt = Date.now();
}

function rememberConfig(cfg, source) {
  if (!cfg || typeof cfg !== "object") return;
  state.trace.configEvents.push({
    eventTime: Date.now(),
    source: String(source || ""),
    config: cloneJsonSafe(cfg),
  });
}

function linkExtractionJobToTurn(jobId, turnId) {
  const jid = String(jobId || "").trim();
  if (!jid || !turnId) return;
  state.jobTurnMap[jid] = String(turnId);
}

function recordRetrievalEvent(retrieval, source, turnId) {
  if (!retrieval || typeof retrieval !== "object") return;
  const event = {
    eventTime: Date.now(),
    source: String(source || ""),
    turnId: turnId ? String(turnId) : null,
    retrieval: cloneJsonSafe(retrieval),
  };
  state.trace.retrievalEvents.push(event);
  const turn = getTurn(turnId);
  if (turn) turn.retrieval = cloneJsonSafe(retrieval);
}

function recordExtractionEvent(extraction, source, turnIdHint) {
  if (!extraction || typeof extraction !== "object") return;
  const jobId = String(extraction.job_id || "").trim();
  const mappedTurnId = jobId && state.jobTurnMap[jobId] ? state.jobTurnMap[jobId] : null;
  const turnId = turnIdHint ? String(turnIdHint) : mappedTurnId;
  if (jobId && turnId) linkExtractionJobToTurn(jobId, turnId);
  const event = {
    eventTime: Date.now(),
    source: String(source || ""),
    turnId: turnId || null,
    extraction: cloneJsonSafe(extraction),
  };
  state.trace.extractionEvents.push(event);
  const turn = getTurn(turnId);
  if (turn) turn.extraction = cloneJsonSafe(extraction);
}

function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function truncateTextForDisplay(text, maxChars) {
  const s = String(text || "");
  const max = Math.max(1, Number(maxChars) || 1);
  const chars = Array.from(s);
  if (chars.length <= max) return s;
  return `${chars.slice(0, Math.max(1, max - 3)).join("")}...`;
}

function renderChat() {
  const log = el("chatLog");
  const shouldStick =
    log.scrollTop + log.clientHeight >= log.scrollHeight - 140;
  const parts = [];
  for (const m of state.messages) {
    const role = (m.role || "system").toLowerCase();
    const pending = !!m.pending;
    const contentHtml = pending
      ? `<span class="typing" aria-label="thinking"><span></span><span></span><span></span></span>`
      : escapeHtml(m.content || "");

    if (role === "assistant") {
      const bubbleCls = pending
        ? "chatbubble chatbubble--assistant chatbubble--pending"
        : "chatbubble chatbubble--assistant";
      parts.push(
        `<div class="chatitem chatitem--assistant"><div class="chatavatar" aria-hidden="true">AS</div><div class="${bubbleCls}">${contentHtml}</div></div>`
      );
      continue;
    }

    if (role === "user") {
      const bubbleCls = pending
        ? "chatbubble chatbubble--user chatbubble--pending"
        : "chatbubble chatbubble--user";
      parts.push(
        `<div class="chatitem chatitem--user"><div class="${bubbleCls}">${contentHtml}</div></div>`
      );
      continue;
    }

    const bubbleCls = pending
      ? "chatbubble chatbubble--system chatbubble--pending"
      : "chatbubble chatbubble--system";
    parts.push(
      `<div class="chatitem chatitem--system"><div class="${bubbleCls}">${contentHtml}</div></div>`
    );
  }
  log.innerHTML = parts.join("");
  if (shouldStick) log.scrollTop = log.scrollHeight;
}

function formatHit(hit) {
  const score = typeof hit.score === "number" ? hit.score.toFixed(3) : "-";
  const name = hit.name || "";
  const desc = hit.description || "";
  const id = hit.id || "";
  const source = hit.source || "";
  const version = hit.version ? `v${hit.version}` : "";
  return `
    <div class="hit">
      <div class="hit__top">
        <span class="hit__rank">#${hit.rank}</span>
        <span class="hit__score">${score}</span>
        <span class="hit__name">${escapeHtml(name)}</span>
      </div>
      <div class="hit__meta">
        <span class="hit__pill">${escapeHtml(source)}</span>
        <span class="hit__pill">${escapeHtml(version)}</span>
        <span class="hit__id">${escapeHtml(id)}</span>
      </div>
      <div class="hit__desc">${escapeHtml(desc)}</div>
    </div>
  `;
}

function renderRetrieval(retrieval) {
  const originalFull = String(retrieval?.original_query || "");
  const originalShort = truncateTextForDisplay(originalFull, 50);
  el("origQuery").textContent = originalShort;
  el("origQuery").title = originalFull;
  el("rewrittenQuery").textContent = retrieval?.rewritten_query || "";
  el("searchQuery").textContent = retrieval?.search_query || "";
  const t = retrieval?.event_time ? _fmtTime(_toMs(retrieval.event_time)) : "";
  el("retrievalAt").textContent = t;

  const hits = Array.isArray(retrieval?.hits) ? retrieval.hits : [];
  const selectedIds = Array.isArray(retrieval?.selected_for_context_ids)
    ? retrieval.selected_for_context_ids
    : [];
  const selectedNames = [];
  for (const id of selectedIds) {
    const h = hits.find((x) => x.id === id);
    selectedNames.push(h ? `${h.name} (${id})` : id);
  }
  el("selectedSkills").textContent = selectedNames.join(", ");
  el("contextInjected").textContent = retrieval?.context_injected ? "true" : "false";

  const err = retrieval?.error ? String(retrieval.error) : "";
  el("retrievalError").textContent = err;

  el("hits").innerHTML = hits.map(formatHit).join("");
}

function pulseRetrievalCard() {
  const card = el("retrievalCard");
  if (!card) return;
  card.classList.remove("card--pulse");
  // Force a reflow to restart the animation when retrieval updates rapidly.
  // eslint-disable-next-line no-unused-expressions
  card.offsetWidth;
  card.classList.add("card--pulse");
  if (state.retrievalPulseTimer) {
    window.clearTimeout(state.retrievalPulseTimer);
    state.retrievalPulseTimer = null;
  }
  state.retrievalPulseTimer = window.setTimeout(() => {
    card.classList.remove("card--pulse");
    state.retrievalPulseTimer = null;
  }, 900);
}

function _toMs(raw) {
  if (typeof raw === "number" && Number.isFinite(raw)) return Math.floor(raw);
  const s = String(raw || "").trim();
  if (!s) return Date.now();
  const t = Date.parse(s);
  return Number.isFinite(t) ? t : Date.now();
}

function _fmtTime(ms) {
  if (!ms || !Number.isFinite(ms)) return "";
  const d = new Date(ms);
  return d.toLocaleTimeString([], { hour12: false });
}

function _fmtElapsed(ms) {
  if (!Number.isFinite(ms) || ms < 0) return "";
  const sec = Math.floor(ms / 1000);
  const s = sec % 60;
  const mTotal = Math.floor(sec / 60);
  const m = mTotal % 60;
  const h = Math.floor(mTotal / 60);
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function _clearExtractionTimers() {
  if (state.extractionRunningTimer) {
    window.clearTimeout(state.extractionRunningTimer);
    state.extractionRunningTimer = null;
  }
  if (state.extractionElapsedTimer) {
    window.clearInterval(state.extractionElapsedTimer);
    state.extractionElapsedTimer = null;
  }
}

function _setExtractionProgress(status, widthPct) {
  const fill = el("extractProgressFill");
  if (!fill) return;
  const pct = Math.max(0, Math.min(100, Number(widthPct) || 0));
  fill.style.width = `${pct}%`;
  fill.className = "extract-progress__fill";
  if (status) fill.classList.add(`extract-progress__fill--${status}`);
}

function _renderExtractionTimes() {
  const started = state.extractionStartedAtMs;
  const finished = state.extractionFinishedAtMs;
  el("extractStartedAt").textContent = started ? _fmtTime(started) : "";
  el("extractFinishedAt").textContent = finished ? _fmtTime(finished) : "";

  let elapsed = "";
  if (started) {
    const end = finished || Date.now();
    elapsed = _fmtElapsed(Math.max(0, end - started));
  }
  el("extractElapsed").textContent = elapsed;
}

function _startElapsedTickerIfNeeded() {
  if (state.extractionElapsedTimer) {
    window.clearInterval(state.extractionElapsedTimer);
    state.extractionElapsedTimer = null;
  }
  if (!state.extractionStartedAtMs) {
    _renderExtractionTimes();
    return;
  }
  const live = state.extractionStatus === "scheduled" || state.extractionStatus === "running";
  _renderExtractionTimes();
  if (!live) return;
  state.extractionElapsedTimer = window.setInterval(() => {
    _renderExtractionTimes();
  }, 1000);
}

function _scheduleRunningTransition(jobId) {
  if (state.extractionRunningTimer) {
    window.clearTimeout(state.extractionRunningTimer);
    state.extractionRunningTimer = null;
  }
  // Keep this hook for backward compatibility, but do not synthesize "running" state in UI.
  // Extraction status should follow backend events only (scheduled/running/completed/failed).
  void jobId;
}

function normalizeExtractionStatus(extraction) {
  const raw = String(extraction?.status || "").trim().toLowerCase();
  if (raw === "scheduled" || raw === "running" || raw === "completed" || raw === "failed") {
    return raw;
  }
  if (extraction?.error) return "failed";
  return "completed";
}

function setExtractionState(status) {
  const node = el("extractState");
  if (!node) return;
  const s = String(status || "").trim().toLowerCase();
  if (!s) {
    node.textContent = "";
    node.className = "kv__v";
    return;
  }
  node.textContent = s;
  node.className = `kv__v state-chip state-chip--${s}`;
}

function renderExtraction(extraction) {
  if (!extraction) {
    _clearExtractionTimers();
    state.extractionJobId = null;
    state.extractionStatus = "";
    state.extractionStartedAtMs = null;
    state.extractionFinishedAtMs = null;
    el("extractTrigger").textContent = "";
    setExtractionState("");
    _setExtractionProgress("", 0);
    _renderExtractionTimes();
    el("extractionError").textContent = "";
    el("upserted").innerHTML = "";
    el("editingSkill").textContent = "";
    el("saveSkillStatus").textContent = "";
    el("saveSkillBtn").disabled = true;
    el("rollbackSkillBtn").disabled = true;
    el("deleteSkillBtn").disabled = true;
    el("skillMdEditor").value = "";
    state.editingSkillId = null;
    state.skillEditorDirty = false;
    return;
  }
  const status = normalizeExtractionStatus(extraction);
  const jobId = String(extraction?.job_id || "").trim();
  const eventTime = _toMs(extraction?.event_time);
  const hasCurrentJob = !!state.extractionJobId;
  const isNewScheduled = status === "scheduled" && !!jobId && jobId !== state.extractionJobId;

  if (isNewScheduled || (!hasCurrentJob && status === "scheduled")) {
    _clearExtractionTimers();
    state.extractionJobId = jobId || `job-${eventTime}`;
    state.extractionStatus = "scheduled";
    state.extractionStartedAtMs = eventTime;
    state.extractionFinishedAtMs = null;
    setExtractionState("scheduled");
    _setExtractionProgress("scheduled", 18);
    _startElapsedTickerIfNeeded();
    _scheduleRunningTransition(state.extractionJobId);
  } else {
    if (jobId && hasCurrentJob && jobId !== state.extractionJobId) {
      // Ignore stale events from older extraction jobs.
      return;
    }
    if (!hasCurrentJob) {
      state.extractionJobId = jobId || `job-${eventTime}`;
      state.extractionStartedAtMs = eventTime;
    }
    state.extractionStatus = status;
    if (!state.extractionStartedAtMs) state.extractionStartedAtMs = eventTime;
    if (status === "running") {
      setExtractionState("running");
      _setExtractionProgress("running", 64);
      _startElapsedTickerIfNeeded();
    } else if (status === "completed") {
      _clearExtractionTimers();
      state.extractionFinishedAtMs = eventTime;
      setExtractionState("completed");
      _setExtractionProgress("completed", 100);
      _startElapsedTickerIfNeeded();
    } else if (status === "failed") {
      _clearExtractionTimers();
      state.extractionFinishedAtMs = eventTime;
      setExtractionState("failed");
      _setExtractionProgress("failed", 100);
      _startElapsedTickerIfNeeded();
    } else {
      setExtractionState(status);
      _setExtractionProgress(status, 18);
      _startElapsedTickerIfNeeded();
    }
  }

  el("extractTrigger").textContent = extraction.trigger || "";
  el("extractionError").textContent = extraction.error ? String(extraction.error) : "";

  const upserted = Array.isArray(extraction.upserted) ? extraction.upserted : [];
  if (!upserted.length) {
    el("upserted").innerHTML = `<div class="muted">(no skills upserted)</div>`;
  } else {
    el("upserted").innerHTML = upserted
      .map(
        (s) =>
          `<div class="upsert"><div class="upsert__name">${escapeHtml(
            s.name || ""
          )}</div><div class="upsert__meta">${escapeHtml(s.id || "")} · v${escapeHtml(
            s.version || ""
          )} · ${escapeHtml(s.owner || "")}</div></div>`
      )
      .join("");
  }

  const mdItems = Array.isArray(extraction.skill_mds) ? extraction.skill_mds : [];
  if (!mdItems.length) {
    const id = state.editingSkillId || "";
    el("editingSkill").textContent = id;
    const busy = state.savingSkill || state.deletingSkill || state.rollingBackSkill;
    el("saveSkillBtn").disabled = !id || busy;
    el("rollbackSkillBtn").disabled = !id || busy;
    el("deleteSkillBtn").disabled = !id || busy;
    return;
  }
  const item0 = mdItems.length ? mdItems[0] : null;
  const id = item0 && item0.id ? String(item0.id) : "";
  const md = item0 ? String(item0.md || "") : "";

  el("editingSkill").textContent = id || "";
  const busy = state.savingSkill || state.deletingSkill || state.rollingBackSkill;
  el("saveSkillBtn").disabled = !id || busy;
  el("rollbackSkillBtn").disabled = !id || busy;
  el("deleteSkillBtn").disabled = !id || busy;

  // Avoid clobbering in-progress user edits unless this is a new skill.
  if (!id) return;
  if (state.editingSkillId !== id || !state.skillEditorDirty) {
    el("skillMdEditor").value = md;
    state.editingSkillId = id;
    state.skillEditorDirty = false;
    el("saveSkillStatus").textContent = "";
  }
}

function renderConfig(cfg) {
  if (!cfg) return;
  el("minScore").textContent = cfg.min_score != null ? String(cfg.min_score) : "-";
  el("topK").textContent = cfg.top_k != null ? String(cfg.top_k) : "-";
  el("scopeSelect").value = cfg.skill_scope || "all";
  el("rewriteSelect").value = cfg.rewrite_mode || "always";
  el("extractSelect").value = cfg.extract_mode || "auto";
  if (el("extractEveryInput")) {
    const n = cfg.extract_turn_limit != null ? Number(cfg.extract_turn_limit) : 1;
    el("extractEveryInput").value = Number.isFinite(n) && n >= 1 ? String(Math.floor(n)) : "1";
  }
}

async function api(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = json?.error || `HTTP ${res.status}`;
    throw new Error(err);
  }
  return json;
}

function _tsCompact() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(
    d.getMinutes()
  )}${pad(d.getSeconds())}`;
}

function downloadJsonFile(fileName, payload) {
  const text = JSON.stringify(payload, null, 2);
  const blob = new Blob([text], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function collectExtractedSkillIds() {
  const ids = new Set();
  const events = Array.isArray(state.trace.extractionEvents) ? state.trace.extractionEvents : [];
  for (const ev of events) {
    const ex = ev && ev.extraction && typeof ev.extraction === "object" ? ev.extraction : null;
    if (!ex) continue;
    const upserted = Array.isArray(ex.upserted) ? ex.upserted : [];
    for (const s of upserted) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
    const skillMds = Array.isArray(ex.skill_mds) ? ex.skill_mds : [];
    for (const s of skillMds) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
  }
  return Array.from(ids);
}

async function exportSessionJson() {
  const sid = await ensureSession();
  let sessionState = null;
  let extractedSkillSnapshots = [];
  try {
    const out = await api("/api/session/state", { session_id: sid });
    sessionState = out?.state || null;
  } catch (_e) {
    sessionState = null;
  }

  try {
    const skillIds = collectExtractedSkillIds();
    if (skillIds.length) {
      const out2 = await api("/api/skills/get_many", {
        session_id: sid,
        skill_ids: skillIds,
      });
      extractedSkillSnapshots = Array.isArray(out2?.skills) ? out2.skills : [];
    }
  } catch (_e) {
    extractedSkillSnapshots = [];
  }

  const payload = {
    exported_at: new Date().toISOString(),
    session_id: sid,
    ui_state: {
      extraction_job_id: state.extractionJobId || null,
      extraction_status: state.extractionStatus || "",
      extraction_started_at_ms: state.extractionStartedAtMs || null,
      extraction_finished_at_ms: state.extractionFinishedAtMs || null,
      editing_skill_id: state.editingSkillId || null,
    },
    session_state: {
      config: cloneJsonSafe(sessionState?.config) || null,
      pending: !!sessionState?.pending,
      messages: cloneJsonSafe(sessionState?.messages) || cloneJsonSafe(state.messages) || [],
    },
    process: {
      trace_started_at_ms: state.trace.sessionStartedAt || null,
      turns: cloneJsonSafe(state.trace.turns) || [],
      retrieval_events: cloneJsonSafe(state.trace.retrievalEvents) || [],
      extraction_events: cloneJsonSafe(state.trace.extractionEvents) || [],
      extracted_skill_snapshots: cloneJsonSafe(extractedSkillSnapshots) || [],
      config_events: cloneJsonSafe(state.trace.configEvents) || [],
      last_result: cloneJsonSafe(state.lastResult),
    },
  };

  const fileName = `autoskill-session-${String(sid || "").slice(0, 8) || "local"}-${_tsCompact()}.json`;
  downloadJsonFile(fileName, payload);
  setStatus(true, "exported");
}

async function ensureSession() {
  if (state.sessionId) return state.sessionId;
  const out = await api("/api/session/new", {});
  state.sessionId = out.session_id;
  state.trace = {
    sessionStartedAt: Date.now(),
    turns: [],
    retrievalEvents: [],
    extractionEvents: [],
    configEvents: [],
  };
  state.turnSeq = 0;
  state.turnById = Object.create(null);
  state.jobTurnMap = Object.create(null);
  el("sessionBadge").textContent = `session: ${state.sessionId.slice(0, 8)}`;
  setStatus(true, "connected");

  const msgs = Array.isArray(out?.state?.messages) ? out.state.messages : [];
  state.messages = msgs;
  renderChat();
  renderConfig(out?.state?.config);
  rememberConfig(out?.state?.config, "session/new");
  return state.sessionId;
}

async function pollSession() {
  if (!state.sessionId) return;
  try {
    const out = await api("/api/session/poll", { session_id: state.sessionId });
    const events = out?.events?.extraction;
    if (Array.isArray(events) && events.length) {
      for (const ev of events) {
        recordExtractionEvent(ev, "poll", null);
      }
      renderExtraction(events[events.length - 1]);
    }
  } catch (_e) {
    // Best-effort: polling should not disrupt chat UX.
  }
}

function startPolling() {
  if (state.pollTimer) return;
  state.pollTimer = window.setInterval(() => {
    pollSession();
  }, 1200);
}

async function apiStreamNdjson(path, body, onEvent) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });

  if (!res.ok) {
    const json = await res.json().catch(() => ({}));
    const err = json?.error || `HTTP ${res.status}`;
    throw new Error(err);
  }
  if (!res.body) {
    throw new Error("Streaming response body is unavailable in this environment.");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    while (true) {
      const idx = buffer.indexOf("\n");
      if (idx < 0) break;
      const line = buffer.slice(0, idx).trim();
      buffer = buffer.slice(idx + 1);
      if (!line) continue;
      let obj = null;
      try {
        obj = JSON.parse(line);
      } catch (_e) {
        obj = null;
      }
      if (obj && typeof onEvent === "function") onEvent(obj);
    }
  }

  buffer += decoder.decode();
  const tail = buffer.trim();
  if (tail) {
    try {
      const obj = JSON.parse(tail);
      if (obj && typeof onEvent === "function") onEvent(obj);
    } catch (_e) {
      // Ignore non-JSON tail.
    }
  }
}

function applySendResult(result, streamAssistantIndex, turnId) {
  state.lastResult = cloneJsonSafe(result);
  const append = Array.isArray(result?.chat_append) ? result.chat_append : [];
  if (result?.kind === "command" && result?.command === "/clear") {
    state.messages = append.length ? append.slice() : [];
    renderChat();
    renderRetrieval(null);
    renderExtraction(null);
  } else if (result?.kind === "chat") {
    let assistantObj = null;
    if (append.length >= 2) {
      assistantObj = append[1];
    } else if (append.length === 1 && String(append[0]?.role || "") === "assistant") {
      assistantObj = append[0];
    }
    if (assistantObj) {
      if (
        Number.isInteger(streamAssistantIndex) &&
        streamAssistantIndex >= 0 &&
        streamAssistantIndex < state.messages.length &&
        String(state.messages[streamAssistantIndex]?.role || "") === "assistant"
      ) {
        state.messages[streamAssistantIndex] = { role: "assistant", content: assistantObj.content || "" };
      } else {
        state.messages.push(assistantObj);
      }
      renderChat();
    }
  } else if (append.length) {
    state.messages.push(...append);
    renderChat();
  }

  if (result?.retrieval) {
    recordRetrievalEvent(result.retrieval, "result", turnId);
    renderRetrieval(result.retrieval);
  }
  if (result?.extraction) {
    recordExtractionEvent(result.extraction, "result", turnId);
    const jid = String(result?.extraction?.job_id || "").trim();
    if (jid) linkExtractionJobToTurn(jid, turnId);
    renderExtraction(result.extraction);
  }
  if (result?.config) {
    renderConfig(result.config);
    rememberConfig(result.config, "result");
  }

  const patch = {
    kind: String(result?.kind || "unknown"),
    command: String(result?.command || ""),
    chatAppend: cloneJsonSafe(append) || [],
    retrieval: result?.retrieval ? cloneJsonSafe(result.retrieval) : null,
    extraction: result?.extraction ? cloneJsonSafe(result.extraction) : null,
    error: "",
  };
  finishTurn(turnId, patch);
}

async function sendText(text) {
  const sid = await ensureSession();
  if (state.inFlight) return;
  const turn = newTurn(text);
  const turnId = turn.id;
  state.inFlight = true;

  const sendBtn = el("sendBtn");
  const input = el("chatInput");
  const extractBtn = el("extractBtn");
  const helpBtn = el("helpBtn");
  const clearBtn = el("clearBtn");
  const exportBtn = el("exportBtn");
  sendBtn.disabled = true;
  if (extractBtn) extractBtn.disabled = true;
  if (helpBtn) helpBtn.disabled = true;
  if (clearBtn) clearBtn.disabled = true;
  if (exportBtn) exportBtn.disabled = true;

  // Optimistic UI: show the user message immediately + a typing indicator.
  state.messages.push({ role: "user", content: text });
  state.messages.push({ role: "assistant", content: "", pending: true });
  renderChat();
  setStatus(true, "streaming...");

  try {
    let streamAssistantIndex = -1;
    let streamStarted = false;
    let result = null;

    const ensureAssistantBubble = () => {
      if (streamAssistantIndex >= 0) return;
      while (state.messages.length && state.messages[state.messages.length - 1]?.pending) {
        state.messages.pop();
      }
      state.messages.push({ role: "assistant", content: "" });
      streamAssistantIndex = state.messages.length - 1;
    };

    try {
      await apiStreamNdjson(
        "/api/session/input_stream",
        { session_id: sid, text },
        (ev) => {
          const t = String(ev?.type || "").trim().toLowerCase();
          if (t === "meta") {
            streamStarted = true;
            return;
          }
          if (t === "assistant_delta") {
            streamStarted = true;
            const delta = String(ev?.delta || "");
            if (!delta) return;
            ensureAssistantBubble();
            state.messages[streamAssistantIndex].content += delta;
            renderChat();
            return;
          }
          if (t === "retrieval") {
            const payload = ev?.retrieval || null;
            recordRetrievalEvent(payload, "stream", turnId);
            renderRetrieval(payload);
            pulseRetrievalCard();
            return;
          }
          if (t === "extraction") {
            const payload = ev?.extraction || null;
            recordExtractionEvent(payload, "stream", turnId);
            const jid = String(payload?.job_id || "").trim();
            if (jid) linkExtractionJobToTurn(jid, turnId);
            renderExtraction(payload);
            return;
          }
          if (t === "result") {
            result = ev?.result || {};
            return;
          }
          if (t === "error") {
            const err = String(ev?.error || "unknown stream error");
            throw new Error(err);
          }
        }
      );
    } catch (e) {
      // Fallback for old backends that do not provide stream endpoint.
      if (!streamStarted) {
        const out = await api("/api/session/input", { session_id: sid, text });
        result = out?.result || {};
      } else {
        throw e;
      }
    }

    while (state.messages.length && state.messages[state.messages.length - 1]?.pending) {
      state.messages.pop();
    }
    if (!result || typeof result !== "object") {
      throw new Error("Missing final result from stream.");
    }
    applySendResult(result, streamAssistantIndex, turnId);
    // Force a near-immediate extraction event sync after this turn so the right panel can
    // transition to completed/failed without waiting for the next timer tick.
    await pollSession();
    window.setTimeout(() => {
      pollSession();
    }, 900);

    setStatus(true, "connected");
  } catch (e) {
    // Remove typing indicator and show error as a system message.
    while (state.messages.length && state.messages[state.messages.length - 1]?.pending) {
      state.messages.pop();
    }
    state.messages.push({ role: "system", content: `Error: ${String(e?.message || e)}` });
    renderChat();
    setStatus(false, String(e?.message || e));
    finishTurn(turnId, {
      kind: "error",
      command: "",
      chatAppend: [],
      retrieval: null,
      extraction: null,
      error: String(e?.message || e),
    });
  } finally {
    state.inFlight = false;
    sendBtn.disabled = false;
    if (extractBtn) extractBtn.disabled = false;
    if (helpBtn) helpBtn.disabled = false;
    if (clearBtn) clearBtn.disabled = false;
    if (exportBtn) exportBtn.disabled = false;
    input.focus();
  }
}

function autoGrowTextarea(textarea) {
  if (!textarea) return;
  textarea.style.height = "auto";
  const maxPx = 180;
  const next = Math.min(textarea.scrollHeight, maxPx);
  textarea.style.height = `${next}px`;
  textarea.style.overflowY = textarea.scrollHeight > maxPx ? "auto" : "hidden";
}

function bind() {
  const triggerSend = async (text) => {
    if (state.inFlight) return;
    const t = String(text || "");
    if (!t.trim()) return;
    try {
      await sendText(t);
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  };

  el("sendBtn").addEventListener("click", async () => {
    const t = el("chatInput").value;
    if (!t.trim()) return;
    el("chatInput").value = "";
    autoGrowTextarea(el("chatInput"));
    await triggerSend(t);
  });

  el("chatInput").addEventListener("keydown", async (ev) => {
    if (ev.key !== "Enter") return;
    if (ev.shiftKey) return; // newline
    ev.preventDefault();
    if (state.inFlight) return;
    el("sendBtn").click();
  });

  el("chatInput").addEventListener("input", () => {
    autoGrowTextarea(el("chatInput"));
  });

  el("helpBtn").addEventListener("click", async () => {
    await triggerSend("/help");
  });

  el("clearBtn").addEventListener("click", async () => {
    await triggerSend("/clear");
  });

  if (el("exportBtn")) {
    el("exportBtn").addEventListener("click", async () => {
      if (state.inFlight) return;
      try {
        await exportSessionJson();
      } catch (e) {
        setStatus(false, String(e?.message || e));
      }
    });
  }

  el("extractBtn").addEventListener("click", async () => {
    const hint = el("extractHintInput")?.value || "";
    const cmd = hint && hint.trim() ? `extract_now ${hint.trim()}` : "extract_now";
    await triggerSend(cmd);
    if (el("extractHintInput")) el("extractHintInput").value = "";
  });

  if (el("extractHintInput")) {
    el("extractHintInput").addEventListener("keydown", (ev) => {
      if (ev.key !== "Enter") return;
      ev.preventDefault();
      el("extractBtn").click();
    });
  }

  if (el("skillMdEditor")) {
    el("skillMdEditor").addEventListener("input", () => {
      state.skillEditorDirty = true;
      if (el("saveSkillStatus")) el("saveSkillStatus").textContent = "unsaved changes";
    });
  }

  if (el("saveSkillBtn")) {
    el("saveSkillBtn").addEventListener("click", async () => {
      const sid = await ensureSession();
      const skillId = state.editingSkillId;
      const md = el("skillMdEditor")?.value || "";
      if (!skillId) return;
      if (state.savingSkill) return;
      state.savingSkill = true;
      el("saveSkillBtn").disabled = true;
      if (el("rollbackSkillBtn")) el("rollbackSkillBtn").disabled = true;
      if (el("deleteSkillBtn")) el("deleteSkillBtn").disabled = true;
      el("saveSkillStatus").textContent = "saving...";
      try {
        const out = await api("/api/skill/save_md", {
          session_id: sid,
          skill_id: skillId,
          skill_md: md,
        });
        const md2 = out?.skill_md != null ? String(out.skill_md) : md;
        el("skillMdEditor").value = md2;
        state.skillEditorDirty = false;
        el("saveSkillStatus").textContent = "saved";
        el("editingSkill").textContent = out?.skill?.id ? String(out.skill.id) : skillId;
      } catch (e) {
        el("saveSkillStatus").textContent = `save failed: ${String(e?.message || e)}`;
        setStatus(false, String(e?.message || e));
      } finally {
        state.savingSkill = false;
        el("saveSkillBtn").disabled = !state.editingSkillId;
        if (el("rollbackSkillBtn")) el("rollbackSkillBtn").disabled = !state.editingSkillId;
        if (el("deleteSkillBtn")) el("deleteSkillBtn").disabled = !state.editingSkillId;
      }
    });
  }

  if (el("rollbackSkillBtn")) {
    el("rollbackSkillBtn").addEventListener("click", async () => {
      const sid = await ensureSession();
      const skillId = state.editingSkillId;
      if (!skillId) return;
      if (state.rollingBackSkill) return;

      const ok = window.confirm(
        "Rollback this skill to the previous saved version?\n\nThis will overwrite current editor content."
      );
      if (!ok) return;

      state.rollingBackSkill = true;
      el("rollbackSkillBtn").disabled = true;
      if (el("saveSkillBtn")) el("saveSkillBtn").disabled = true;
      if (el("deleteSkillBtn")) el("deleteSkillBtn").disabled = true;
      el("saveSkillStatus").textContent = "rolling back...";
      try {
        const out = await api("/api/skill/rollback_prev", {
          session_id: sid,
          skill_id: skillId,
        });
        const md = out?.skill_md != null ? String(out.skill_md) : "";
        if (el("skillMdEditor")) el("skillMdEditor").value = md;
        state.skillEditorDirty = false;
        const outId = out?.skill?.id ? String(out.skill.id) : skillId;
        state.editingSkillId = outId;
        el("editingSkill").textContent = outId;
        const ver = out?.skill?.version ? String(out.skill.version) : "";
        el("saveSkillStatus").textContent = ver ? `rolled back to v${ver}` : "rolled back";
      } catch (e) {
        el("saveSkillStatus").textContent = `rollback failed: ${String(e?.message || e)}`;
        setStatus(false, String(e?.message || e));
      } finally {
        state.rollingBackSkill = false;
        const hasSkill = !!state.editingSkillId;
        if (el("rollbackSkillBtn")) el("rollbackSkillBtn").disabled = !hasSkill;
        if (el("saveSkillBtn")) el("saveSkillBtn").disabled = !hasSkill;
        if (el("deleteSkillBtn")) el("deleteSkillBtn").disabled = !hasSkill;
      }
    });
  }

  if (el("deleteSkillBtn")) {
    el("deleteSkillBtn").addEventListener("click", async () => {
      const sid = await ensureSession();
      const skillId = state.editingSkillId;
      if (!skillId) return;
      if (state.deletingSkill) return;
      const ok = window.confirm(
        `Delete this skill from local storage?\n\n${skillId}\n\nThis cannot be undone.`
      );
      if (!ok) return;

      state.deletingSkill = true;
      el("deleteSkillBtn").disabled = true;
      el("saveSkillBtn").disabled = true;
      if (el("rollbackSkillBtn")) el("rollbackSkillBtn").disabled = true;
      el("saveSkillStatus").textContent = "deleting...";
      try {
        await api("/api/skill/delete", { session_id: sid, skill_id: skillId });
        el("saveSkillStatus").textContent = "deleted";
        el("editingSkill").textContent = "";
        el("skillMdEditor").value = "";
        state.editingSkillId = null;
        state.skillEditorDirty = false;
      } catch (e) {
        el("saveSkillStatus").textContent = `delete failed: ${String(e?.message || e)}`;
        setStatus(false, String(e?.message || e));
      } finally {
        state.deletingSkill = false;
        el("deleteSkillBtn").disabled = true;
        if (el("rollbackSkillBtn")) el("rollbackSkillBtn").disabled = true;
        el("saveSkillBtn").disabled = true;
      }
    });
  }

  el("scopeSelect").addEventListener("change", async () => {
    const v = el("scopeSelect").value;
    const cmd = v === "library" ? "/scope common" : `/scope ${v}`;
    try {
      await sendText(cmd);
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });

  el("rewriteSelect").addEventListener("change", async () => {
    const v = el("rewriteSelect").value;
    try {
      await sendText(`/rewrite ${v}`);
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });

  el("extractSelect").addEventListener("change", async () => {
    const v = el("extractSelect").value;
    try {
      await sendText(`/extract ${v}`);
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });

  el("extractEveryInput").addEventListener("change", async () => {
    const raw = el("extractEveryInput").value;
    let n = Number.parseInt(String(raw || "1"), 10);
    if (!Number.isFinite(n) || n < 1) n = 1;
    el("extractEveryInput").value = String(n);
    try {
      await sendText(`/extract_every ${n}`);
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });
}

window.addEventListener("load", async () => {
  bind();
  try {
    await ensureSession();
    startPolling();
    autoGrowTextarea(el("chatInput"));
  } catch (e) {
    setStatus(false, String(e?.message || e));
  }
});
