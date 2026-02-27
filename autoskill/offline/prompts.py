"""
Standalone prompt builders for offline extraction channels.

Important:
- Offline channels use these full prompts directly.
- They do NOT reuse online chat prompt bodies.
"""

from __future__ import annotations

from typing import Optional


OFFLINE_CHANNEL_DOC = "offline_extract_from_doc"
OFFLINE_CHANNEL_CONV = "offline_extract_from_conversation"
OFFLINE_CHANNEL_TRAJ = "offline_extract_from_agentic_trajectory"

_OFFLINE_CHANNELS = {
    OFFLINE_CHANNEL_DOC,
    OFFLINE_CHANNEL_CONV,
    OFFLINE_CHANNEL_TRAJ,
}


def is_offline_channel(channel: str) -> bool:
    return str(channel or "").strip().lower() in _OFFLINE_CHANNELS


def build_offline_extract_prompt(*, channel: str, max_candidates: int) -> str:
    ch = str(channel or "").strip().lower()
    if ch == OFFLINE_CHANNEL_DOC:
        return (
            "You are AutoSkill's Offline Document Skill Extractor.\n"
            "Task: extract reusable skills from document excerpts.\n"
            "Output ONLY strict JSON parseable by json.loads.\n"
            "\n"
            "Evidence model:\n"
            "- Treat document text as authoritative evidence.\n"
            "- Extract only reusable policy/procedure/workflow/output-contract constraints.\n"
            "- Do not extract case anecdotes, narrative background, or topic facts only.\n"
            "\n"
            "Extraction rules:\n"
            "- Keep HOW-to-do and acceptance checks, not this-instance WHAT.\n"
            "- Keep hard limits, mandatory steps, validation checkpoints, safety constraints.\n"
            "- Remove one-off entities (org/person/project/url/id/date/budget).\n"
            "- If content cannot generalize after de-identification, output {\"skills\": []}.\n"
            "- If no durable method/policy signal, output {\"skills\": []}.\n"
            "\n"
            f"Return schema: {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
            "Fields per skill:\n"
            "- name: intent + action + domain, concise and searchable.\n"
            "- description: 1-2 sentences, what/when to use.\n"
            "- prompt: executable Markdown with # Goal, # Constraints & Style, optional # Workflow.\n"
            "- triggers: 3-5 intent phrases.\n"
            "- tags: 1-6 canonical keywords.\n"
            "- examples: 0-3 short de-identified examples.\n"
            "- confidence: 0.0-1.0.\n"
            "Language: all fields must follow dominant input language.\n"
            "JSON validity: escape newlines as \\n. No Markdown code block.\n"
        )
    if ch == OFFLINE_CHANNEL_CONV:
        return (
            "You are AutoSkill's Offline Conversation Skill Extractor.\n"
            "Task: extract reusable skills from archived multi-turn conversations.\n"
            "Output ONLY strict JSON parseable by json.loads.\n"
            "\n"
            "Evidence model:\n"
            "- USER turns are primary evidence; ASSISTANT turns are supporting context.\n"
            "- Keep user-confirmed constraints/preferences/policies.\n"
            "- Ignore assistant-only inventions unless user explicitly confirms.\n"
            "\n"
            "Recency and topic:\n"
            "- Prioritize recent turns for active intent.\n"
            "- Detect boundary turn (new objective/deliverable/channel/task).\n"
            "- If boundary exists, use post-boundary intent and do not mix stale constraints.\n"
            "- If no boundary, preserve stable constraints across turns.\n"
            "\n"
            "Extraction rules:\n"
            "- Extract when reusable policy/process constraints are present (single explicit durable rule can be enough).\n"
            "- Do not extract one-off content edits without reusable policy value.\n"
            "- Keep must-do and must-not-do constraints.\n"
            "- Remove one-off entities; generalize with placeholders when needed.\n"
            "- If reusable signal is weak, output {\"skills\": []}.\n"
            "\n"
            f"Return schema: {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
            "Fields per skill:\n"
            "- name: encode user intent + action + domain/platform when evidenced.\n"
            "- description: 1-2 sentences, what/when to use.\n"
            "- prompt: executable Markdown with # Goal, # Constraints & Style, optional # Workflow.\n"
            "- triggers: 3-5 deduplicated intent phrases.\n"
            "- tags: 1-6 canonical keywords.\n"
            "- examples: 0-3 short de-identified examples.\n"
            "- confidence: 0.0-1.0.\n"
            "Language: all fields must follow dominant input language.\n"
            "JSON validity: escape newlines as \\n. No Markdown code block.\n"
        )
    if ch == OFFLINE_CHANNEL_TRAJ:
        return (
            "You are AutoSkill's Offline Agentic-Trajectory Skill Extractor.\n"
            "Task: extract reusable agent workflow skills from trajectories (messages/events/tool-use).\n"
            "Output ONLY strict JSON parseable by json.loads.\n"
            "\n"
            "Evidence model:\n"
            "- Successful trajectory patterns and explicit user constraints are valid evidence.\n"
            "- Prefer reusable tool orchestration policy over one-run results.\n"
            "- Ignore transient runtime artifacts and environment-specific payload.\n"
            "\n"
            "Extraction rules:\n"
            "- Capture ordered workflow, checkpoints, fallback/retry, stop/rollback conditions.\n"
            "- Keep output contract and validation criteria.\n"
            "- Keep only durable constraints; remove IDs, paths, timestamps, one-run values.\n"
            "- If workflow identity is unclear or not reusable, output {\"skills\": []}.\n"
            "\n"
            f"Return schema: {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
            "Fields per skill:\n"
            "- name: intent + action + workflow domain/tool context when identity-critical.\n"
            "- description: 1-2 sentences, what/when to use.\n"
            "- prompt: executable Markdown with # Goal, # Constraints & Style, optional # Workflow.\n"
            "- triggers: 3-5 deduplicated intent phrases.\n"
            "- tags: 1-6 canonical keywords.\n"
            "- examples: 0-3 short de-identified examples.\n"
            "- confidence: 0.0-1.0.\n"
            "Language: all fields must follow dominant input language.\n"
            "JSON validity: escape newlines as \\n. No Markdown code block.\n"
        )
    return ""


def build_offline_repair_prompt(*, channel: str, max_candidates: int) -> str:
    ch = str(channel or "").strip().lower()
    if ch == OFFLINE_CHANNEL_DOC:
        label = "document"
    elif ch == OFFLINE_CHANNEL_CONV:
        label = "conversation"
    elif ch == OFFLINE_CHANNEL_TRAJ:
        label = "trajectory"
    else:
        return ""
    return (
        f"You are a JSON output fixer for offline {label} skill extraction.\n"
        "Given DATA and DRAFT, output ONLY strict JSON: {\"skills\": [...]}.\n"
        f"Return at most {max_candidates} skills; if uncertain return {{\"skills\": []}}.\n"
        "No Markdown, no commentary.\n"
        "Preserve only reusable, de-identified capability/policy/workflow signals.\n"
        "Drop one-off entities and non-portable payload.\n"
        "Keep schema fields: name, description, prompt, triggers, tags, examples, confidence.\n"
        "Language must follow dominant input language.\n"
        "JSON validity: escape newlines as \\n.\n"
    )


def build_offline_manage_decide_prompt(channel: str) -> str:
    ch = str(channel or "").strip().lower()
    if ch == OFFLINE_CHANNEL_DOC:
        focus = (
            "document-derived candidates: compare reusable procedure/protocol identity, not topical text overlap"
        )
    elif ch == OFFLINE_CHANNEL_CONV:
        focus = (
            "conversation-derived candidates: compare user-intent continuity and durable policy constraints"
        )
    elif ch == OFFLINE_CHANNEL_TRAJ:
        focus = (
            "trajectory-derived candidates: compare workflow identity, tool orchestration pattern, and completion criteria"
        )
    else:
        return ""
    return (
        "You are AutoSkill's Offline Skill Set Manager.\n"
        "Task: decide add/merge/discard for a newly extracted candidate given similar skills.\n"
        "Output ONLY strict JSON; no Markdown or extra text.\n"
        f"Channel focus: {focus}.\n"
        "\n"
        "Quality objective: high-signal, low-fragmentation skill set.\n"
        "Actions:\n"
        "- add: create new user skill\n"
        "- merge: merge into ONE existing user skill (target_skill_id)\n"
        "- discard: do not store candidate\n"
        "\n"
        "Decision rules:\n"
        "- Prefer discard for weak/generic/non-portable candidates.\n"
        "- Prefer merge when same capability identity and candidate is an incremental improvement.\n"
        "- Prefer add only for distinct objective/deliverable/operation class/completion criteria.\n"
        "- Do not merge purely due wording/name/example overlap.\n"
        "- Similarity score is a hint, not sole criterion.\n"
        "\n"
        "Return schema:\n"
        "{\n"
        "  \"action\": \"add\"|\"merge\"|\"discard\",\n"
        "  \"target_skill_id\": string|null,\n"
        "  \"reason\": string\n"
        "}\n"
    )


def build_offline_merge_gate_prompt(channel: str) -> str:
    ch = str(channel or "").strip().lower()
    if ch == OFFLINE_CHANNEL_DOC:
        focus = "procedure/protocol identity"
    elif ch == OFFLINE_CHANNEL_CONV:
        focus = "recent user-intent continuity and durable policy identity"
    elif ch == OFFLINE_CHANNEL_TRAJ:
        focus = "agent workflow/tool orchestration identity"
    else:
        return ""
    return (
        "You are AutoSkill's Offline Capability Identity Judge.\n"
        "Task: decide whether candidate_skill is the SAME capability as existing_skill.\n"
        "Output ONLY strict JSON.\n"
        f"Primary comparison axis: {focus}.\n"
        "Return same_capability=true only if objective + deliverable + operation class + acceptance criteria align.\n"
        "If uncertain, return same_capability=false.\n"
        "Return schema:\n"
        "{\n"
        "  \"same_capability\": true|false,\n"
        "  \"confidence\": 0.0-1.0,\n"
        "  \"reason\": \"short reason\"\n"
        "}\n"
    )


def build_offline_merge_prompt(channel: str) -> str:
    ch = str(channel or "").strip().lower()
    if ch not in _OFFLINE_CHANNELS:
        return ""
    return (
        "You are AutoSkill's Offline Skill Merger.\n"
        "Task: merge existing_skill and candidate_skill into ONE improved skill.\n"
        "Output ONLY strict JSON parseable by json.loads.\n"
        "\n"
        "Rules:\n"
        "- Preserve capability identity; do not change job-to-be-done.\n"
        "- Perform semantic union, not concatenation.\n"
        "- Deduplicate triggers/tags/examples by meaning.\n"
        "- Keep durable reusable constraints and checks from both sides.\n"
        "- Remove one-off payload/entities and conflicting stale constraints.\n"
        "- If candidate adds no durable value, keep existing content mostly unchanged.\n"
        "\n"
        "Output fields ONLY:\n"
        "{name, description, prompt, triggers, tags, examples}\n"
        "Field expectations:\n"
        "- name: concise, searchable, stable intent identity.\n"
        "- description: 1-2 sentences, what/when to use.\n"
        "- prompt: executable Markdown (# Goal, # Constraints & Style, optional # Workflow).\n"
        "- triggers: 3-5 deduplicated intent phrases.\n"
        "- tags: 1-6 canonical keywords.\n"
        "- examples: 0-3 short de-identified examples.\n"
        "\n"
        "JSON validity: escape newlines as \\n.\n"
    )


def maybe_offline_prompt(
    *,
    channel: str,
    kind: str,
    max_candidates: Optional[int] = None,
) -> str:
    ch = str(channel or "").strip().lower()
    k = str(kind or "").strip().lower()
    if not is_offline_channel(ch):
        return ""
    if k == "extract":
        return build_offline_extract_prompt(channel=ch, max_candidates=int(max_candidates or 1))
    if k == "repair":
        return build_offline_repair_prompt(channel=ch, max_candidates=int(max_candidates or 1))
    if k == "manage_decide":
        return build_offline_manage_decide_prompt(ch)
    if k == "merge_gate":
        return build_offline_merge_gate_prompt(ch)
    if k == "merge":
        return build_offline_merge_prompt(ch)
    return ""
