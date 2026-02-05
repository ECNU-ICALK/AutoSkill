/* global fetch */

const state = {
  sessionId: null,
  messages: [],
  lastResult: null,
  inFlight: false,
  savingSkill: false,
  deletingSkill: false,
  editingSkillId: null,
  skillEditorDirty: false,
  pollTimer: null,
};

function el(id) {
  return document.getElementById(id);
}

function setStatus(ok, text) {
  const badge = el("statusBadge");
  badge.textContent = text;
  badge.className = ok ? "badge badge--ok" : "badge badge--err";
}

function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderChat() {
  const log = el("chatLog");
  const parts = [];
  for (const m of state.messages) {
    const role = (m.role || "system").toLowerCase();
    const cls =
      role === "user"
        ? "msg msg--user"
        : role === "assistant"
        ? "msg msg--assistant"
        : "msg msg--system";
    const pending = !!m.pending;
    const cls2 = pending ? `${cls} msg--pending` : cls;
    const roleLabel =
      role === "user" ? "You" : role === "assistant" ? "Assistant" : "System";
    const contentHtml = pending
      ? `<span class="typing" aria-label="thinking"><span></span><span></span><span></span></span>`
      : escapeHtml(m.content || "");
    parts.push(
      `<div class="${cls2}"><div class="msg__role">${escapeHtml(
        roleLabel
      )}</div><div class="msg__content">${contentHtml}</div></div>`
    );
  }
  log.innerHTML = parts.join("");
  log.scrollTop = log.scrollHeight;
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
  el("origQuery").textContent = retrieval?.original_query || "";
  el("rewrittenQuery").textContent = retrieval?.rewritten_query || "";
  el("searchQuery").textContent = retrieval?.search_query || "";

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

function renderExtraction(extraction) {
  if (!extraction) {
    el("extractTrigger").textContent = "";
    el("extractionError").textContent = "";
    el("upserted").innerHTML = "";
    el("editingSkill").textContent = "";
    el("saveSkillStatus").textContent = "";
    el("saveSkillBtn").disabled = true;
    el("deleteSkillBtn").disabled = true;
    el("skillMdEditor").value = "";
    state.editingSkillId = null;
    state.skillEditorDirty = false;
    return;
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
    el("saveSkillBtn").disabled = !id || state.savingSkill;
    el("deleteSkillBtn").disabled = !id || state.deletingSkill;
    return;
  }
  const item0 = mdItems.length ? mdItems[0] : null;
  const id = item0 && item0.id ? String(item0.id) : "";
  const md = item0 ? String(item0.md || "") : "";

  el("editingSkill").textContent = id || "";
  el("saveSkillBtn").disabled = !id || state.savingSkill;
  el("deleteSkillBtn").disabled = !id || state.deletingSkill;

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

async function ensureSession() {
  if (state.sessionId) return state.sessionId;
  const out = await api("/api/session/new", {});
  state.sessionId = out.session_id;
  el("sessionBadge").textContent = `session: ${state.sessionId.slice(0, 8)}`;
  setStatus(true, "connected");

  const msgs = Array.isArray(out?.state?.messages) ? out.state.messages : [];
  state.messages = msgs;
  renderChat();
  renderConfig(out?.state?.config);
  return state.sessionId;
}

async function pollSession() {
  if (!state.sessionId) return;
  if (state.inFlight) return;
  try {
    const out = await api("/api/session/poll", { session_id: state.sessionId });
    const events = out?.events?.extraction;
    if (Array.isArray(events) && events.length) {
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

async function sendText(text) {
  const sid = await ensureSession();
  if (state.inFlight) return;
  state.inFlight = true;

  const sendBtn = el("sendBtn");
  const input = el("chatInput");
  sendBtn.disabled = true;
  input.disabled = true;

  // Optimistic UI: show the user message immediately + a typing indicator.
  state.messages.push({ role: "user", content: text });
  state.messages.push({ role: "assistant", content: "", pending: true });
  renderChat();
  setStatus(true, "thinking...");

  try {
    const out = await api("/api/session/input", { session_id: sid, text });
    const result = out.result || {};

    // Remove typing indicator.
    while (state.messages.length && state.messages[state.messages.length - 1]?.pending) {
      state.messages.pop();
    }

    const append = Array.isArray(result.chat_append) ? result.chat_append : [];
    if (result.kind === "command" && result.command === "/clear") {
      state.messages = append.length ? append.slice() : [];
      renderChat();
      renderRetrieval(null);
      renderExtraction(null);
    } else if (result.kind === "chat") {
      // Server returns [user, assistant]. We already rendered the user message optimistically, so only append assistant.
      if (append.length >= 2) {
        state.messages.push(append[1]);
      } else if (append.length === 1) {
        state.messages.push(append[0]);
      }
      renderChat();
    } else if (append.length) {
      // Commands typically return system messages.
      state.messages.push(...append);
      renderChat();
    }

    if (result.retrieval) renderRetrieval(result.retrieval);
    if (result.extraction) renderExtraction(result.extraction);
    if (result.config) renderConfig(result.config);

    setStatus(true, "connected");
  } catch (e) {
    // Remove typing indicator and show error as a system message.
    while (state.messages.length && state.messages[state.messages.length - 1]?.pending) {
      state.messages.pop();
    }
    state.messages.push({ role: "system", content: `Error: ${String(e?.message || e)}` });
    renderChat();
    setStatus(false, String(e?.message || e));
  } finally {
    state.inFlight = false;
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

function bind() {
  el("sendBtn").addEventListener("click", async () => {
    const t = el("chatInput").value;
    if (!t.trim()) return;
    el("chatInput").value = "";
    try {
      await sendText(t);
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });

  el("chatInput").addEventListener("keydown", async (ev) => {
    if (ev.key !== "Enter") return;
    if (ev.shiftKey) return; // newline
    ev.preventDefault();
    el("sendBtn").click();
  });

  el("helpBtn").addEventListener("click", async () => {
    try {
      await sendText("/help");
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });

  el("clearBtn").addEventListener("click", async () => {
    try {
      await sendText("/clear");
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
  });

  el("extractBtn").addEventListener("click", async () => {
    const hint = el("extractHintInput")?.value || "";
    const cmd = hint && hint.trim() ? `extract_now ${hint.trim()}` : "extract_now";
    try {
      await sendText(cmd);
      if (el("extractHintInput")) el("extractHintInput").value = "";
    } catch (e) {
      setStatus(false, String(e?.message || e));
    }
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
        if (el("deleteSkillBtn")) el("deleteSkillBtn").disabled = !state.editingSkillId;
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
  } catch (e) {
    setStatus(false, String(e?.message || e));
  }
});
