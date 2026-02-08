/* global fetch */

const state = {
  sessionId: null,
  sessionList: [],
  sessionRuntime: Object.create(null),
  selectedTurnId: null,
  messages: [],
  lastResult: null,
  inFlight: false,
  savingSkill: false,
  deletingSkill: false,
  rollingBackSkill: false,
  hydratingSkillId: null,
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

function makeEmptyTrace() {
  return {
    sessionStartedAt: Date.now(),
    turns: [],
    retrievalEvents: [],
    extractionEvents: [],
    configEvents: [],
  };
}

function latestPayloadFromTrace(traceObj, primaryBucket, fallbackBucket, payloadKey) {
  if (!traceObj || typeof traceObj !== "object") return null;
  const arrRaw = traceObj[primaryBucket];
  const arrAlt = traceObj[fallbackBucket];
  const arr = Array.isArray(arrRaw) ? arrRaw : Array.isArray(arrAlt) ? arrAlt : [];
  for (let i = arr.length - 1; i >= 0; i -= 1) {
    const ev = arr[i];
    const payload = ev && typeof ev === "object" ? ev[payloadKey] : null;
    if (payload && typeof payload === "object") {
      return cloneJsonSafe(payload);
    }
  }
  return null;
}

function setStatus(ok, text) {
  const badge = el("statusBadge");
  badge.textContent = text;
  badge.className = ok ? "badge badge--ok" : "badge badge--err";
}

function snapshotCurrentSessionRuntime() {
  const sid = String(state.sessionId || "").trim();
  if (!sid) return;
  state.sessionRuntime[sid] = {
    messages: cloneJsonSafe(state.messages) || [],
    selectedTurnId: state.selectedTurnId || null,
    lastResult: cloneJsonSafe(state.lastResult),
    extractionJobId: state.extractionJobId || null,
    extractionStatus: state.extractionStatus || "",
    extractionStartedAtMs: state.extractionStartedAtMs || null,
    extractionFinishedAtMs: state.extractionFinishedAtMs || null,
    editingSkillId: state.editingSkillId || null,
    skillEditorDirty: !!state.skillEditorDirty,
    turnSeq: Number(state.turnSeq || 0),
    turnById: cloneJsonSafe(state.turnById) || {},
    jobTurnMap: cloneJsonSafe(state.jobTurnMap) || {},
    trace: cloneJsonSafe(state.trace) || makeEmptyTrace(),
  };
}

function restoreSessionRuntime(sid, serverState, serverTrace = null) {
  const key = String(sid || "").trim();
  const snap = state.sessionRuntime[key];
  _clearExtractionTimers();
  if (snap && typeof snap === "object") {
    state.messages = Array.isArray(snap.messages) ? snap.messages : [];
    state.selectedTurnId = snap.selectedTurnId || null;
    state.lastResult = snap.lastResult || null;
    state.extractionJobId = snap.extractionJobId || null;
    state.extractionStatus = snap.extractionStatus || "";
    state.extractionStartedAtMs = snap.extractionStartedAtMs || null;
    state.extractionFinishedAtMs = snap.extractionFinishedAtMs || null;
    state.editingSkillId = snap.editingSkillId || null;
    state.skillEditorDirty = !!snap.skillEditorDirty;
    state.turnSeq = Number(snap.turnSeq || 0);
    state.turnById = snap.turnById && typeof snap.turnById === "object" ? snap.turnById : Object.create(null);
    state.jobTurnMap = snap.jobTurnMap && typeof snap.jobTurnMap === "object" ? snap.jobTurnMap : Object.create(null);
    state.trace = snap.trace && typeof snap.trace === "object" ? snap.trace : makeEmptyTrace();
  } else {
    const traceFromServer = normalizeTraceForExport(serverTrace);
    const msgs = Array.isArray(serverState?.messages) ? serverState.messages : [];
    state.messages = msgs;
    state.selectedTurnId = null;
    state.lastResult = cloneJsonSafe(traceFromServer?.lastResult) || null;
    state.extractionJobId = null;
    state.extractionStatus = "";
    state.extractionStartedAtMs = null;
    state.extractionFinishedAtMs = null;
    state.editingSkillId = null;
    state.skillEditorDirty = false;
    state.turnSeq = 0;
    state.turnById = Object.create(null);
    state.jobTurnMap = Object.create(null);
    state.trace = traceFromServer && typeof traceFromServer === "object" ? traceFromServer : makeEmptyTrace();
    if (serverState?.config) rememberConfig(serverState.config, "session/state");
  }
  renderChat();
  const latestRetrieval =
    latestPayloadFromTrace(state.trace, "retrievalEvents", "retrieval_events", "retrieval") ||
    (state.lastResult && state.lastResult.retrieval ? cloneJsonSafe(state.lastResult.retrieval) : null);
  renderRetrieval(latestRetrieval);

  const latestExtraction =
    latestPayloadFromTrace(state.trace, "extractionEvents", "extraction_events", "extraction") ||
    (state.lastResult && state.lastResult.extraction ? cloneJsonSafe(state.lastResult.extraction) : null);
  if (latestExtraction) {
    renderExtraction(latestExtraction);
  } else {
    const ts = state.extractionFinishedAtMs || state.extractionStartedAtMs || Date.now();
    if (state.extractionStatus) {
      renderExtraction({
        trigger: "",
        job_id: state.extractionJobId || "",
        event_time: ts,
        status: state.extractionStatus,
        error: "",
        upserted: [],
        skill_mds: [],
      });
    } else {
      renderExtraction(null);
    }
  }
  if (serverState?.config) renderConfig(serverState.config);
}

function formatSessionTime(ms) {
  if (!ms || !Number.isFinite(ms)) return "";
  const d = new Date(ms);
  return d.toLocaleTimeString([], { hour12: false });
}

function renderSessionList() {
  const list = el("sessionList");
  if (!list) return;
  const rows = Array.isArray(state.sessionList) ? state.sessionList : [];
  if (!rows.length) {
    list.innerHTML = `<div class="muted">(no sessions)</div>`;
    return;
  }
  const cur = String(state.sessionId || "").trim();
  list.innerHTML = rows
    .map((s) => {
      const sid = String(s.id || "");
      const active = sid && sid === cur;
      const title = String(s.title || "New Chat");
      const preview = String(s.preview || "");
      const updated = formatSessionTime(Number(s.updated_at_ms || 0));
      const count = Number(s.message_count || 0);
      return `
        <div class="session-item ${active ? "session-item--active" : ""}">
          <button class="session-item__main" type="button" data-session-id="${escapeHtml(sid)}">
            <div class="session-item__title">${escapeHtml(title)}</div>
            <div class="session-item__meta">${escapeHtml(updated)} · ${count} msg</div>
            <div class="session-item__preview">${escapeHtml(preview)}</div>
          </button>
          <div class="session-item__actions">
            <button
              class="session-item__action session-item__action--export"
              type="button"
              data-session-export-id="${escapeHtml(sid)}"
              title="Export session JSON"
              aria-label="Export session JSON"
            >Export</button>
            <button
              class="session-item__action session-item__action--delete"
              type="button"
              data-session-delete-id="${escapeHtml(sid)}"
              title="Delete session"
              aria-label="Delete session"
            >×</button>
          </div>
        </div>
      `;
    })
    .join("");
}

async function refreshSessionList() {
  const out = await api("/api/session/list", {});
  state.sessionList = Array.isArray(out?.sessions) ? out.sessions : [];
  renderSessionList();
}

async function createNewSession(overrides) {
  snapshotCurrentSessionRuntime();
  const out = await api("/api/session/new", { config: overrides || {} });
  const sid = String(out?.session_id || "").trim();
  if (!sid) {
    throw new Error("failed to create session");
  }
  state.sessionId = sid;
  const serverState = out?.state || null;
  state.sessionList = Array.isArray(out?.sessions) ? out.sessions : [];
  restoreSessionRuntime(sid, serverState, out?.trace || null);
  renderSessionList();
  el("sessionBadge").textContent = `session: ${state.sessionId.slice(0, 8)}`;
  return sid;
}

async function switchSession(sid) {
  const nextId = String(sid || "").trim();
  if (!nextId) return;
  if (state.sessionId === nextId) return;

  snapshotCurrentSessionRuntime();
  const out = await api("/api/session/state", { session_id: nextId });
  state.sessionId = nextId;
  const serverState = out?.state || null;
  restoreSessionRuntime(nextId, serverState, out?.trace || null);
  state.sessionList = Array.isArray(out?.sessions) ? out.sessions : state.sessionList;
  renderSessionList();
  el("sessionBadge").textContent = `session: ${state.sessionId.slice(0, 8)}`;
}

async function deleteSession(sid) {
  const targetId = String(sid || "").trim();
  if (!targetId) return;
  const row = (Array.isArray(state.sessionList) ? state.sessionList : []).find(
    (s) => String(s?.id || "").trim() === targetId
  );
  const title = String(row?.title || "this session");
  const ok = window.confirm(`Delete "${title}"? This cannot be undone.`);
  if (!ok) return;

  snapshotCurrentSessionRuntime();
  const currentId = String(state.sessionId || "").trim();
  const out = await api("/api/session/delete", { session_id: targetId });

  delete state.sessionRuntime[targetId];
  state.sessionList = Array.isArray(out?.sessions) ? out.sessions : [];

  if (currentId !== targetId) {
    renderSessionList();
    return;
  }

  const nextId = String(out?.next_session_id || "").trim();
  if (nextId) {
    state.sessionId = nextId;
    restoreSessionRuntime(nextId, out?.state || null, out?.trace || null);
    renderSessionList();
    el("sessionBadge").textContent = `session: ${state.sessionId.slice(0, 8)}`;
    return;
  }

  state.sessionId = null;
  restoreSessionRuntime("", { messages: [] });
  renderSessionList();
  el("sessionBadge").textContent = "session: -";
  await createNewSession({});
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

function chatActionIcon(action) {
  const a = String(action || "").trim().toLowerCase();
  if (a === "copy") {
    return `<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="10" height="10" rx="2"></rect><rect x="5" y="5" width="10" height="10" rx="2"></rect></svg>`;
  }
  if (a === "regenerate") {
    return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8 8 0 1 0 2 5.3"></path><path d="M20 4v7h-7"></path></svg>`;
  }
  if (a === "view-turn") {
    return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"></path><circle cx="12" cy="12" r="2.6"></circle></svg>`;
  }
  return "";
}

function chatActionButton(action, attrs, label) {
  const a = String(action || "").trim().toLowerCase();
  const extra = String(attrs || "");
  const title = escapeHtml(String(label || a || ""));
  return `<button class="chatbubble__action" type="button" data-chat-action="${a}" title="${title}" aria-label="${title}"${extra}>${chatActionIcon(
    a
  )}</button>`;
}

function truncateTextForDisplay(text, maxChars) {
  const s = String(text || "");
  const max = Math.max(1, Number(maxChars) || 1);
  const chars = Array.from(s);
  if (chars.length <= max) return s;
  return `${chars.slice(0, Math.max(1, max - 3)).join("")}...`;
}

async function copyTextToClipboard(text) {
  const value = String(text || "");
  if (!value) return;
  try {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      await navigator.clipboard.writeText(value);
      return;
    }
  } catch (_e) {
    // Fallback below.
  }
  const node = document.createElement("textarea");
  node.value = value;
  node.setAttribute("readonly", "readonly");
  node.style.position = "fixed";
  node.style.opacity = "0";
  document.body.appendChild(node);
  node.select();
  try {
    document.execCommand("copy");
  } finally {
    document.body.removeChild(node);
  }
}

function previousUserMessageText(beforeIndex) {
  const idx = Number.isInteger(beforeIndex) ? beforeIndex : -1;
  for (let i = idx - 1; i >= 0; i -= 1) {
    const m = state.messages[i];
    if (!m || typeof m !== "object") continue;
    const role = String(m.role || "").trim().toLowerCase();
    if (role !== "user") continue;
    const content = String(m.content || "").trim();
    if (content) return content;
  }
  return "";
}

function normalizeForMatch(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function traceTurns() {
  const turns = state.trace && typeof state.trace === "object" ? state.trace.turns : null;
  return Array.isArray(turns) ? turns : [];
}

function turnIdOf(turn) {
  if (!turn || typeof turn !== "object") return "";
  return String(turn.id || turn.turn_id || "").trim();
}

function turnInputOf(turn) {
  if (!turn || typeof turn !== "object") return "";
  return String(turn.input || "").trim();
}

function turnChatAppendOf(turn) {
  if (!turn || typeof turn !== "object") return [];
  const a = turn.chatAppend;
  if (Array.isArray(a)) return a;
  const b = turn.chat_append;
  if (Array.isArray(b)) return b;
  return [];
}

function assistantTextFromTurn(turn) {
  const append = turnChatAppendOf(turn);
  for (let i = append.length - 1; i >= 0; i -= 1) {
    const msg = append[i];
    if (!msg || typeof msg !== "object") continue;
    const role = String(msg.role || "").trim().toLowerCase();
    if (role !== "assistant") continue;
    const content = String(msg.content || "").trim();
    if (content) return content;
  }
  return "";
}

function traceTurnById(turnId) {
  const tid = String(turnId || "").trim();
  if (!tid) return null;
  const turns = traceTurns();
  for (const t of turns) {
    if (turnIdOf(t) === tid) return t;
  }
  return null;
}

function traceEventTurnId(ev) {
  if (!ev || typeof ev !== "object") return "";
  return String(ev.turnId || ev.turn_id || "").trim();
}

function traceEventPayload(ev, payloadKey) {
  if (!ev || typeof ev !== "object") return null;
  const p = ev[payloadKey];
  if (p && typeof p === "object") return p;
  return null;
}

function traceEvents(primaryBucket, fallbackBucket) {
  if (!state.trace || typeof state.trace !== "object") return [];
  const a = state.trace[primaryBucket];
  if (Array.isArray(a)) return a;
  const b = state.trace[fallbackBucket];
  if (Array.isArray(b)) return b;
  return [];
}

function extractionJobIdOf(extraction) {
  if (!extraction || typeof extraction !== "object") return "";
  return String(extraction.job_id || extraction.jobId || "").trim();
}

function extractionEventTimeOf(extraction) {
  if (!extraction || typeof extraction !== "object") return Date.now();
  const raw =
    extraction.event_time != null ? extraction.event_time : extraction.eventTime != null ? extraction.eventTime : null;
  return _toMs(raw);
}

function extractionArrayOf(extraction, snakeKey, camelKey) {
  if (!extraction || typeof extraction !== "object") return [];
  const a = extraction[snakeKey];
  if (Array.isArray(a)) return a;
  if (camelKey) {
    const b = extraction[camelKey];
    if (Array.isArray(b)) return b;
  }
  return [];
}

function extractionPayloadScore(extraction) {
  if (!extraction || typeof extraction !== "object") return -1;
  const status = normalizeExtractionStatus(extraction);
  let score = 0;
  if (status === "completed") score += 40;
  else if (status === "failed") score += 30;
  else if (status === "running") score += 20;
  else if (status === "scheduled") score += 10;

  const upserted = extractionArrayOf(extraction, "upserted", "upserted");
  const skillMds = extractionArrayOf(extraction, "skill_mds", "skillMds");
  const skills = extractionArrayOf(extraction, "skills", "skills");
  if (upserted.length) score += 20;
  if (skillMds.length) score += 30;
  if (skills.length) score += 15;
  if (String(extraction.error || "").trim()) score += 5;
  return score;
}

function latestExtractionPayloadByJobId(jobId) {
  const jid = String(jobId || "").trim();
  if (!jid) return null;
  const events = traceEvents("extractionEvents", "extraction_events");
  for (let i = events.length - 1; i >= 0; i -= 1) {
    const ev = events[i];
    const payload = traceEventPayload(ev, "extraction");
    if (!payload || typeof payload !== "object") continue;
    if (extractionJobIdOf(payload) !== jid) continue;
    return cloneJsonSafe(payload);
  }
  return null;
}

function bestExtractionPayloadForTurn(turnId, turnObj) {
  const turn = turnObj && typeof turnObj === "object" ? turnObj : traceTurnById(turnId);
  const candidates = [];

  const fromTurn = payloadFromTurn(turn, "extraction");
  if (fromTurn) candidates.push(fromTurn);

  const fromTurnEvent = latestTurnPayload(turnId, "extraction");
  if (fromTurnEvent) candidates.push(fromTurnEvent);

  const turnJobId = extractionJobIdOf(fromTurn || (turn && turn.extraction));
  if (turnJobId) {
    const fromJob = latestExtractionPayloadByJobId(turnJobId);
    if (fromJob) candidates.push(fromJob);
  }

  if (!candidates.length) return null;

  let best = candidates[0];
  let bestScore = extractionPayloadScore(best);
  let bestTime = extractionEventTimeOf(best);
  for (let i = 1; i < candidates.length; i += 1) {
    const cur = candidates[i];
    const score = extractionPayloadScore(cur);
    const ts = extractionEventTimeOf(cur);
    if (score > bestScore || (score === bestScore && ts >= bestTime)) {
      best = cur;
      bestScore = score;
      bestTime = ts;
    }
  }
  return cloneJsonSafe(best);
}

function latestTurnPayload(turnId, payloadKey) {
  const tid = String(turnId || "").trim();
  if (!tid) return null;
  const eventBuckets =
    payloadKey === "retrieval"
      ? ["retrievalEvents", "retrieval_events"]
      : ["extractionEvents", "extraction_events"];
  const events = traceEvents(eventBuckets[0], eventBuckets[1]);
  for (let i = events.length - 1; i >= 0; i -= 1) {
    const ev = events[i];
    if (traceEventTurnId(ev) !== tid) continue;
    const payload = traceEventPayload(ev, payloadKey);
    if (payload && typeof payload === "object") {
      return cloneJsonSafe(payload);
    }
  }
  return null;
}

function payloadFromTurn(turn, payloadKey) {
  if (!turn || typeof turn !== "object") return null;
  const v = turn[payloadKey];
  if (v && typeof v === "object") return cloneJsonSafe(v);
  return null;
}

function buildMessageTurnIndexMap() {
  const out = Object.create(null);
  const turns = traceTurns();
  const msgs = Array.isArray(state.messages) ? state.messages : [];
  if (!turns.length || !msgs.length) return out;

  let cursor = 0;
  for (const turn of turns) {
    const tid = turnIdOf(turn);
    if (!tid) continue;

    const expectedUser = normalizeForMatch(turnInputOf(turn));
    if (expectedUser) {
      for (let i = cursor; i < msgs.length; i += 1) {
        const m = msgs[i];
        if (!m || typeof m !== "object") continue;
        const role = String(m.role || "").trim().toLowerCase();
        if (role !== "user") continue;
        const content = normalizeForMatch(m.content || "");
        if (content !== expectedUser) continue;
        out[i] = tid;
        cursor = i + 1;
        break;
      }
    }

    const expectedAssistant = normalizeForMatch(assistantTextFromTurn(turn));
    if (expectedAssistant) {
      for (let i = cursor; i < msgs.length; i += 1) {
        const m = msgs[i];
        if (!m || typeof m !== "object") continue;
        const role = String(m.role || "").trim().toLowerCase();
        if (role !== "assistant") continue;
        const content = normalizeForMatch(m.content || "");
        if (content !== expectedAssistant) continue;
        out[i] = tid;
        cursor = i + 1;
        break;
      }
    }
  }
  return out;
}

function loadTurnDiagnostics(turnId) {
  const tid = String(turnId || "").trim();
  if (!tid) return;
  const turn = traceTurnById(tid);
  const retrieval =
    payloadFromTurn(turn, "retrieval") ||
    latestTurnPayload(tid, "retrieval");
  const extraction = bestExtractionPayloadForTurn(tid, turn);

  state.selectedTurnId = tid;
  renderChat();
  renderRetrieval(retrieval);
  renderExtraction(extraction, { force: true });
}

function renderChat() {
  const log = el("chatLog");
  const shouldStick =
    log.scrollTop + log.clientHeight >= log.scrollHeight - 140;
  const parts = [];
  const msgTurnMap = buildMessageTurnIndexMap();
  let latestAssistantIndex = -1;
  for (let i = state.messages.length - 1; i >= 0; i -= 1) {
    const cur = state.messages[i];
    if (!cur || typeof cur !== "object") continue;
    const role = String(cur.role || "").trim().toLowerCase();
    if (role === "assistant" && !cur.pending) {
      latestAssistantIndex = i;
      break;
    }
  }

  for (let idx = 0; idx < state.messages.length; idx += 1) {
    const m = state.messages[idx];
    const role = (m.role || "system").toLowerCase();
    const turnId = String(msgTurnMap[idx] || "").trim();
    const turnAttr = turnId ? ` data-turn-id="${escapeHtml(turnId)}" data-msg-index="${idx}"` : "";
    const turnCls = turnId ? " chatitem--turn" : "";
    const activeCls = turnId && turnId === String(state.selectedTurnId || "") ? " chatitem--turn-active" : "";
    const pending = !!m.pending;
    const contentHtml = pending
      ? `<span class="typing" aria-label="thinking"><span></span><span></span><span></span></span>`
      : escapeHtml(m.content || "");

    if (role === "assistant") {
      const bubbleCls = pending
        ? "chatbubble chatbubble--assistant chatbubble--pending"
        : "chatbubble chatbubble--assistant";
      const canCopy = !pending;
      const canRegenerate = !pending && idx === latestAssistantIndex;
      const canViewTurn = !!turnId;
      const actionsHtml =
        canCopy || canRegenerate || canViewTurn
          ? `<div class="chatbubble__actions">
              ${canCopy ? chatActionButton("copy", ` data-msg-index="${idx}"`, "Copy") : ""}
              ${canRegenerate ? chatActionButton("regenerate", ` data-msg-index="${idx}"`, "Regenerate") : ""}
              ${canViewTurn ? chatActionButton("view-turn", ` data-turn-id="${escapeHtml(turnId)}"`, "View Turn") : ""}
            </div>`
          : "";
      parts.push(
        `<div class="chatitem chatitem--assistant${turnCls}${activeCls}"${turnAttr}><div class="chatavatar" aria-hidden="true">AS</div><div class="chatassistant-wrap"><div class="${bubbleCls}">${contentHtml}</div>${actionsHtml}</div></div>`
      );
      continue;
    }

    if (role === "user") {
      const bubbleCls = pending
        ? "chatbubble chatbubble--user chatbubble--pending"
        : "chatbubble chatbubble--user";
      parts.push(
        `<div class="chatitem chatitem--user${turnCls}${activeCls}"${turnAttr}><div class="chatuser-wrap"><div class="${bubbleCls}">${contentHtml}</div></div></div>`
      );
      continue;
    }

    const bubbleCls = pending
      ? "chatbubble chatbubble--system chatbubble--pending"
      : "chatbubble chatbubble--system";
    const canCopy = !pending;
    const canViewTurn = !!turnId;
    const actionsHtml =
      canCopy || canViewTurn
        ? `<div class="chatbubble__actions chatbubble__actions--center">
            ${canCopy ? chatActionButton("copy", ` data-msg-index="${idx}"`, "Copy") : ""}
            ${canViewTurn ? chatActionButton("view-turn", ` data-turn-id="${escapeHtml(turnId)}"`, "View Turn") : ""}
          </div>`
        : "";
    parts.push(
      `<div class="chatitem chatitem--system${turnCls}${activeCls}"${turnAttr}><div class="chatsystem-wrap"><div class="${bubbleCls}">${contentHtml}</div>${actionsHtml}</div></div>`
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

function renderExtraction(extraction, options) {
  const opts = options && typeof options === "object" ? options : {};
  const force = !!opts.force;
  if (!extraction) {
    _clearExtractionTimers();
    state.hydratingSkillId = null;
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
  if (force) {
    _clearExtractionTimers();
    state.extractionJobId = null;
    state.extractionStatus = "";
    state.extractionStartedAtMs = null;
    state.extractionFinishedAtMs = null;
  }
  const status = normalizeExtractionStatus(extraction);
  const jobId = extractionJobIdOf(extraction);
  const eventTime = extractionEventTimeOf(extraction);
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
    if (!force && jobId && hasCurrentJob && jobId !== state.extractionJobId) {
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

  const upsertedRaw = extractionArrayOf(extraction, "upserted", "upserted");
  const detailSkills = extractionArrayOf(extraction, "skills", "skills");
  const upserted =
    upsertedRaw.length > 0
      ? upsertedRaw
      : detailSkills.map((s) => ({
          id: String((s && s.id) || ""),
          name: String((s && s.name) || ""),
          version: String((s && s.version) || ""),
          owner: String((s && (s.owner || s.user_id)) || ""),
        }));
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

  let mdItems = extractionArrayOf(extraction, "skill_mds", "skillMds");
  if (!mdItems.length && detailSkills.length) {
    mdItems = detailSkills
      .map((s) => ({
        id: String((s && s.id) || ""),
        md: String((s && (s.skill_md || s.skillMd)) || ""),
      }))
      .filter((x) => x.id && x.md);
  }
  if (!mdItems.length) {
    const id = upserted.length ? String((upserted[0] && upserted[0].id) || "").trim() : "";
    el("editingSkill").textContent = id;
    if ((!id || state.editingSkillId !== id) && !state.skillEditorDirty) {
      el("skillMdEditor").value = "";
      state.skillEditorDirty = false;
      state.editingSkillId = id || null;
      el("saveSkillStatus").textContent = "";
    }
    const busy = state.savingSkill || state.deletingSkill || state.rollingBackSkill;
    el("saveSkillBtn").disabled = !id || busy;
    el("rollbackSkillBtn").disabled = !id || busy;
    el("deleteSkillBtn").disabled = !id || busy;
    if (id && !state.skillEditorDirty) {
      hydrateSkillEditorFromStore(id);
    }
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

async function hydrateSkillEditorFromStore(skillId) {
  const sid = String(state.sessionId || "").trim();
  const targetId = String(skillId || "").trim();
  if (!sid || !targetId) return;
  if (String(state.hydratingSkillId || "").trim() === targetId) return;
  state.hydratingSkillId = targetId;
  try {
    const out = await api("/api/skills/get_many", { session_id: sid, skill_ids: [targetId] });
    const rows = Array.isArray(out?.skills) ? out.skills : [];
    const hit = rows.find((x) => String(x?.id || "").trim() === targetId) || null;
    const md = String((hit && hit.skill_md) || "").trim();
    if (!md) return;
    if (String(state.editingSkillId || "").trim() !== targetId) return;
    if (state.skillEditorDirty) return;
    el("skillMdEditor").value = md;
    el("saveSkillStatus").textContent = "";
  } catch (_e) {
    // Best-effort hydration; keep UI responsive when API is unavailable.
  } finally {
    if (String(state.hydratingSkillId || "").trim() === targetId) {
      state.hydratingSkillId = null;
    }
  }
}

function normalizeTraceForExport(raw) {
  if (!raw || typeof raw !== "object") {
    return {
      sessionStartedAt: null,
      turns: [],
      retrievalEvents: [],
      extractionEvents: [],
      configEvents: [],
      lastResult: null,
    };
  }
  const started =
    raw.sessionStartedAt != null
      ? raw.sessionStartedAt
      : raw.session_started_at_ms != null
      ? raw.session_started_at_ms
      : null;
  return {
    sessionStartedAt: started,
    turns: cloneJsonSafe(raw.turns) || [],
    retrievalEvents: cloneJsonSafe(raw.retrievalEvents || raw.retrieval_events) || [],
    extractionEvents: cloneJsonSafe(raw.extractionEvents || raw.extraction_events) || [],
    configEvents: cloneJsonSafe(raw.configEvents || raw.config_events) || [],
    lastResult: cloneJsonSafe(raw.lastResult != null ? raw.lastResult : raw.last_result),
  };
}

function collectExtractedSkillIds(traceObj, lastResultObj) {
  const ids = new Set();
  const events = Array.isArray(traceObj?.extractionEvents) ? traceObj.extractionEvents : [];
  for (const ev of events) {
    const ex = ev && ev.extraction && typeof ev.extraction === "object" ? ev.extraction : null;
    if (!ex) continue;
    const upserted = Array.isArray(ex.upserted) ? ex.upserted : [];
    for (const s of upserted) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
    const skillMds = Array.isArray(ex.skill_mds) ? ex.skill_mds : Array.isArray(ex.skillMds) ? ex.skillMds : [];
    for (const s of skillMds) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
    const skills = Array.isArray(ex.skills) ? ex.skills : [];
    for (const s of skills) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
  }
  const lastEx = lastResultObj?.extraction;
  if (lastEx && typeof lastEx === "object") {
    const upserted = Array.isArray(lastEx.upserted) ? lastEx.upserted : [];
    for (const s of upserted) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
    const skillMds = Array.isArray(lastEx.skill_mds)
      ? lastEx.skill_mds
      : Array.isArray(lastEx.skillMds)
      ? lastEx.skillMds
      : [];
    for (const s of skillMds) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
    const skills = Array.isArray(lastEx.skills) ? lastEx.skills : [];
    for (const s of skills) {
      const id = String((s && s.id) || "").trim();
      if (id) ids.add(id);
    }
  }
  return Array.from(ids);
}

async function exportSessionJson(sessionId) {
  const sidIn = String(sessionId || "").trim();
  const sid = sidIn || (await ensureSession());
  const runtime = state.sessionRuntime[sid];
  const isCurrent = sid === String(state.sessionId || "").trim();
  let sessionState = null;
  let sessionTraceRaw = null;
  let extractedSkillSnapshots = [];
  try {
    const out = await api("/api/session/state", { session_id: sid });
    sessionState = out?.state || null;
    sessionTraceRaw = out?.trace || null;
  } catch (_e) {
    sessionState = null;
    sessionTraceRaw = null;
  }

  const traceForExport = isCurrent
    ? normalizeTraceForExport(state.trace)
    : runtime?.trace
    ? normalizeTraceForExport(runtime.trace)
    : normalizeTraceForExport(sessionTraceRaw);
  const lastResultForExport = isCurrent
    ? cloneJsonSafe(state.lastResult)
    : runtime?.lastResult != null
    ? cloneJsonSafe(runtime.lastResult)
    : cloneJsonSafe(traceForExport.lastResult);
  const uiStateForExport = isCurrent
    ? {
        extraction_job_id: state.extractionJobId || null,
        extraction_status: state.extractionStatus || "",
        extraction_started_at_ms: state.extractionStartedAtMs || null,
        extraction_finished_at_ms: state.extractionFinishedAtMs || null,
        editing_skill_id: state.editingSkillId || null,
      }
    : {
        extraction_job_id: runtime?.extractionJobId || null,
        extraction_status: runtime?.extractionStatus || "",
        extraction_started_at_ms: runtime?.extractionStartedAtMs || null,
        extraction_finished_at_ms: runtime?.extractionFinishedAtMs || null,
        editing_skill_id: runtime?.editingSkillId || null,
      };

  try {
    const skillIds = collectExtractedSkillIds(traceForExport, lastResultForExport);
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
    ui_state: uiStateForExport,
    session_state: {
      config: cloneJsonSafe(sessionState?.config) || null,
      pending: !!sessionState?.pending,
      messages: cloneJsonSafe(sessionState?.messages) || [],
    },
    process: {
      trace_started_at_ms: traceForExport.sessionStartedAt || null,
      turns: cloneJsonSafe(traceForExport.turns) || [],
      retrieval_events: cloneJsonSafe(traceForExport.retrievalEvents) || [],
      extraction_events: cloneJsonSafe(traceForExport.extractionEvents) || [],
      extracted_skill_snapshots: cloneJsonSafe(extractedSkillSnapshots) || [],
      config_events: cloneJsonSafe(traceForExport.configEvents) || [],
      last_result: cloneJsonSafe(lastResultForExport),
    },
  };

  const fileName = `autoskill-session-${String(sid || "").slice(0, 8) || "local"}-${_tsCompact()}.json`;
  downloadJsonFile(fileName, payload);
  setStatus(true, "exported");
}

async function ensureSession() {
  if (state.sessionId) return state.sessionId;
  await refreshSessionList();
  if (Array.isArray(state.sessionList) && state.sessionList.length) {
    await switchSession(state.sessionList[0].id);
    setStatus(true, "connected");
    return state.sessionId;
  }
  const sid = await createNewSession({});
  setStatus(true, "connected");
  return sid;
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
  state.selectedTurnId = turnId || null;
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
    try {
      await refreshSessionList();
    } catch (_e) {
      // Best-effort only.
    }

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

  if (el("newSessionBtn")) {
    el("newSessionBtn").addEventListener("click", async () => {
      if (state.inFlight) return;
      try {
        await createNewSession({});
        setStatus(true, "connected");
      } catch (e) {
        setStatus(false, String(e?.message || e));
      }
    });
  }

  if (el("sessionList")) {
    el("sessionList").addEventListener("click", async (ev) => {
      const exportBtn =
        ev.target && ev.target.closest ? ev.target.closest("[data-session-export-id]") : null;
      if (exportBtn) {
        const sid = String(exportBtn.getAttribute("data-session-export-id") || "").trim();
        if (!sid) return;
        if (state.inFlight) return;
        try {
          await exportSessionJson(sid);
        } catch (e) {
          setStatus(false, String(e?.message || e));
        }
        return;
      }

      const deleteBtn =
        ev.target && ev.target.closest ? ev.target.closest("[data-session-delete-id]") : null;
      if (deleteBtn) {
        const sid = String(deleteBtn.getAttribute("data-session-delete-id") || "").trim();
        if (!sid) return;
        if (state.inFlight) return;
        try {
          await deleteSession(sid);
          setStatus(true, "connected");
        } catch (e) {
          setStatus(false, String(e?.message || e));
        }
        return;
      }

      const btn = ev.target && ev.target.closest ? ev.target.closest("[data-session-id]") : null;
      if (!btn) return;
      const sid = String(btn.getAttribute("data-session-id") || "").trim();
      if (!sid) return;
      if (state.inFlight) return;
      try {
        await switchSession(sid);
        setStatus(true, "connected");
      } catch (e) {
        setStatus(false, String(e?.message || e));
      }
    });
  }

  if (el("chatLog")) {
    el("chatLog").addEventListener("click", async (ev) => {
      const btn =
        ev.target && ev.target.closest ? ev.target.closest("[data-chat-action]") : null;
      if (!btn) {
        const userBubble =
          ev.target && ev.target.closest
            ? ev.target.closest(".chatitem--user[data-turn-id] .chatbubble")
            : null;
        if (!userBubble) return;
        const selectedText =
          typeof window.getSelection === "function"
            ? String(window.getSelection() || "").trim()
            : "";
        if (selectedText) return;
        const userItem =
          userBubble.closest && userBubble.closest(".chatitem--user[data-turn-id]");
        const turnId = String(userItem?.getAttribute("data-turn-id") || "").trim();
        if (!turnId) return;
        loadTurnDiagnostics(turnId);
        setStatus(true, "turn loaded");
        return;
      }
      const action = String(btn.getAttribute("data-chat-action") || "").trim().toLowerCase();

      if (action === "view-turn") {
        const turnId = String(btn.getAttribute("data-turn-id") || "").trim();
        if (!turnId) return;
        loadTurnDiagnostics(turnId);
        setStatus(true, "turn loaded");
        return;
      }

      const idx = Number.parseInt(String(btn.getAttribute("data-msg-index") || "-1"), 10);
      if (!Number.isFinite(idx) || idx < 0 || idx >= state.messages.length) return;
      if (state.inFlight) return;

      if (action === "copy") {
        const msg = state.messages[idx];
        const text = String(msg?.content || "");
        if (!text.trim()) return;
        try {
          await copyTextToClipboard(text);
          setStatus(true, "copied");
        } catch (e) {
          setStatus(false, String(e?.message || e));
        }
        return;
      }

      if (action === "regenerate") {
        const sourceText = previousUserMessageText(idx);
        if (!sourceText) {
          setStatus(false, "No previous user query found.");
          return;
        }
        try {
          await sendText(sourceText);
        } catch (e) {
          setStatus(false, String(e?.message || e));
        }
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
