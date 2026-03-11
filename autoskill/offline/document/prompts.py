"""
Standalone prompt builders for offline extraction channels.

Important:
- Offline channels use these prompt bodies directly.
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
    """Run is offline channel."""
    return str(channel or "").strip().lower() in _OFFLINE_CHANNELS


def build_offline_extract_prompt(*, channel: str, max_candidates: int) -> str:
    """Run build offline extract prompt."""
    ch = str(channel or "").strip().lower()

    if ch == OFFLINE_CHANNEL_DOC:
        return (
            "You are AutoSkill's offline DOCUMENT skill extractor.\n"
            "Task: convert document evidence into reusable, executable counseling assets.\n"
            "Output ONLY strict JSON parseable by json.loads.\n\n"
            "Rules:\n"
            "1) One document may produce zero, one, or MANY assets; do not force one asset per paper.\n"
            "2) Extract reusable method/policy/workflow/intervention assets only; do not summarize narrative facts.\n"
            "3) Each asset must stay single-goal: one primary objective, one primary stage, and one primary method family.\n"
            "4) Keep macro_protocol, session_skill, micro_skill, safety_rule, and knowledge_reference separate; never merge macro and micro assets into one item.\n"
            "5) micro_skill means one therapist move or one tightly-coupled mini-sequence; do not package toolkits, full sessions, or multi-step stage workflows as micro_skill.\n"
            "6) safety_rule is mandatory for suicide/self-harm/violence/crisis screening, escalation, safety planning, or referral logic.\n"
            "7) session_skill means one session-phase scaffold; macro_protocol means cross-phase or multi-stage treatment flow.\n"
            "8) De-identify: remove names, IDs, dates, local paths, one-off payload details.\n"
            "9) Keep hard constraints, safety rules, required sequence, therapist moves, and output checks.\n"
            "10) Prefer finer reusable assets when evidence is specific enough, especially micro interventions and safety rules.\n"
            "11) Include 1-3 short therapist-response examples when the source supports them.\n"
            "12) If no durable reusable asset exists, return {\"skills\": []}.\n"
            "13) Keep only assets likely to be reused by the same user/team.\n\n"
            f"Return schema: {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
            "Each skill item fields:\n"
            "- name, description, prompt, triggers, tags\n"
            "- asset_type (macro_protocol|session_skill|micro_skill|safety_rule|knowledge_reference)\n"
            "- granularity (macro|session|micro), objective\n"
            "- domain, task_family, method_family, stage\n"
            "- applicable_signals, intervention_moves, contraindications\n"
            "- workflow_steps, constraints, cautions, output_contract\n"
            "- examples: array of 1-3 short objects like {input, output, notes?}\n"
            "- relation_type (support|constraint|conflict|case_variant), risk_class (low|medium|high)\n"
            "- confidence (0.0-1.0)\n"
            "- optional resources/files (safe relative paths under scripts/, references/, assets/; concise content only)\n\n"
            "Language:\n"
            "- Use one dominant language from the source text for ALL textual fields.\n"
            "- If dominant language is unclear, return {\"skills\": []}.\n\n"
            "JSON validity:\n"
            "- Escape newlines as \\n and escape quotes correctly.\n"
            "- No Markdown wrapper, output raw JSON only.\n"
        )

    if ch == OFFLINE_CHANNEL_CONV:
        return (
            "You are AutoSkill's offline CONVERSATION skill extractor.\n"
            "Task: extract reusable skills from archived conversation data.\n"
            "Output ONLY strict JSON parseable by json.loads.\n\n"
            "Evidence policy:\n"
            "1) USER turns are the only direct evidence for skill content.\n"
            "2) If input has 'Primary User Questions' and 'Full Conversation', prioritize Primary User Questions.\n"
            "3) Assistant text is context only; do not copy assistant-invented rules into skills.\n"
            "4) If user and assistant conflict, follow user requirements.\n\n"
            "Extraction policy:\n"
            "- Extract only when user provides reusable execution rules (format/schema/constraints/SOP/output contract/tooling preference).\n"
            "- A single strong reusable requirement is sufficient.\n"
            "- Do not extract one-off Q&A, topic facts, or session-only payload.\n"
            "- Keep only skills likely to be reused by this same user.\n"
            "- If insufficient reusable evidence, return {\"skills\": []}.\n\n"
            f"Return schema: {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
            "Fields per skill: name, description, prompt, triggers, tags, confidence, optional resources/files.\n"
            "Prompt must be executable Markdown and include reusable rules only.\n"
            "Avoid case-specific entities in any field.\n\n"
            "Language:\n"
            "- Use one dominant language from USER text for all textual fields.\n"
            "- If unclear, return {\"skills\": []}.\n\n"
            "JSON validity:\n"
            "- Escape newlines as \\n and escape quotes correctly.\n"
            "- No Markdown wrapper, output raw JSON only.\n"
        )

    if ch == OFFLINE_CHANNEL_TRAJ:
        return (
            "You are AutoSkill's offline TRAJECTORY skill extractor.\n"
            "Task: extract reusable agent workflow skills from archived trajectories.\n"
            "Output ONLY strict JSON parseable by json.loads.\n\n"
            "Rules:\n"
            "1) Focus on reusable workflow logic: tool orchestration, checkpoints, retries, fallback, validation.\n"
            "2) Keep the dominant success-driving chain; drop incidental/noisy branches.\n"
            "3) De-identify: remove one-run payloads, IDs, local paths, timestamps, and case-only facts.\n"
            "4) If workflow policy is unclear or non-reusable, return {\"skills\": []}.\n"
            "5) Keep only skills likely to be reused by the same user/team.\n\n"
            f"Return schema: {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
            "Fields per skill: name, description, prompt, triggers, tags, confidence, optional resources/files.\n"
            "Prompt should include workflow, constraints, fallback/error handling, and output checks.\n\n"
            "Language:\n"
            "- Use one dominant language from trajectory text for all textual fields.\n"
            "- If unclear, return {\"skills\": []}.\n\n"
            "JSON validity:\n"
            "- Escape newlines as \\n and escape quotes correctly.\n"
            "- No Markdown wrapper, output raw JSON only.\n"
        )

    return ""


def build_offline_repair_prompt(*, channel: str, max_candidates: int) -> str:
    """Run build offline repair prompt."""
    ch = str(channel or "").strip().lower()
    if ch == OFFLINE_CHANNEL_DOC:
        label = "document"
        keep_fields = (
            "name, description, prompt, triggers, tags, asset_type, granularity, objective, "
            "domain, task_family, method_family, stage, applicable_signals, intervention_moves, contraindications, "
            "workflow_steps, constraints, cautions, output_contract, examples, relation_type, risk_class, confidence, "
            "optional resources/files"
        )
    elif ch == OFFLINE_CHANNEL_CONV:
        label = "conversation"
        keep_fields = "name, description, prompt, triggers, tags, confidence, optional resources/files"
    elif ch == OFFLINE_CHANNEL_TRAJ:
        label = "trajectory"
        keep_fields = "name, description, prompt, triggers, tags, confidence, optional resources/files"
    else:
        return ""

    conv_note = ""
    if ch == OFFLINE_CHANNEL_CONV:
        conv_note = (
            "Use USER turns as evidence. If input includes 'Primary User Questions', treat it as main evidence and full conversation as context only.\n"
        )

    return (
        f"You are a JSON fixer for offline {label} skill extraction.\n"
        "Given DATA and DRAFT, output ONLY strict JSON: {\"skills\": [...]} with no commentary.\n"
        f"Return at most {max_candidates} skill(s); if uncertain return {{\"skills\": []}}.\n"
        f"{conv_note}"
        "Keep only reusable, de-identified rules/workflows likely to be reused by the same user/team.\n"
        "Drop one-off facts, entity names, assistant/platform artifacts, and non-portable payload.\n"
        f"Keep schema fields: {keep_fields}.\n"
        "If resources/files exist, keep only concise reusable assets with safe relative paths.\n"
        "Use one dominant language consistently across all textual fields; if unclear return {\"skills\": []}.\n"
        "Ensure JSON validity (escape newlines as \\n).\n"
    )


def build_offline_manage_decide_prompt(channel: str) -> str:
    """Run build offline manage decide prompt."""
    ch = str(channel or "").strip().lower()
    if ch in {"doc", OFFLINE_CHANNEL_DOC}:
        focus = (
            "Channel focus: documents. Prefer MERGE when methodology/workflow is the same and candidate is an incremental improvement; "
            "ADD only for clearly distinct method family or objective."
        )
    elif ch in {"conv", OFFLINE_CHANNEL_CONV}:
        focus = (
            "Channel focus: conversations. Prefer MERGE for evolving user constraints within the same work item; "
            "ADD only when the user establishes a genuinely new reusable task."
        )
    elif ch in {"traj", OFFLINE_CHANNEL_TRAJ}:
        focus = (
            "Channel focus: trajectories. Prefer MERGE for robustness improvements of the same workflow/tool graph; "
            "ADD only for a distinct objective or orchestration pattern."
        )
    else:
        return ""

    return (
        "You are AutoSkill's Offline Skill Set Manager.\n"
        "Task: decide add / merge / discard for candidate_skill against similar existing skills.\n"
        "Output ONLY strict JSON; no Markdown, no extra text.\n\n"
        f"{focus}\n"
        "Global rules:\n"
        "- Prevent fragmentation: same capability should not be added as a new skill.\n"
        "- Name/wording changes alone are not new capabilities.\n"
        "- Use similarity as hint only; rely on objective + deliverable + constraints + success criteria.\n"
        "- If overlap is high but value is low, choose discard.\n"
        "- Prefer quality over recall; when uncertain between add and merge, prefer discard or merge.\n\n"
        "Return schema:\n"
        "{\n"
        "  \"action\": \"add\"|\"merge\"|\"discard\",\n"
        "  \"target_skill_id\": \"string\"|null,\n"
        "  \"reason\": \"short reason\"\n"
        "}\n"
    )


def build_offline_merge_gate_prompt(channel: str) -> str:
    """Run build offline merge gate prompt."""
    ch = str(channel or "").strip().lower()
    if ch in {"doc", OFFLINE_CHANNEL_DOC}:
        focus = "Judge capability identity by method/framework + deliverable objective, not wording."
    elif ch in {"conv", OFFLINE_CHANNEL_CONV}:
        focus = "Judge capability identity by user job-to-be-done + reusable constraints, not session phrasing."
    elif ch in {"traj", OFFLINE_CHANNEL_TRAJ}:
        focus = "Judge capability identity by workflow/tool orchestration objective, not payload instance."
    else:
        return ""

    return (
        "You are AutoSkill's Offline Capability Identity Judge.\n"
        "Task: decide whether candidate_skill and existing_skill are the SAME capability.\n"
        "Output ONLY strict JSON parseable by json.loads.\n\n"
        f"{focus}\n"
        "Rules:\n"
        "- Ignore surface wording differences.\n"
        "- Incremental refinements/robustness updates are usually same capability.\n"
        "- If objective, deliverable class, audience, or evaluation criteria changes materially, they are different capabilities.\n"
        "- If uncertain, default to same_capability=false.\n\n"
        "Return schema:\n"
        "{\n"
        "  \"same_capability\": true|false,\n"
        "  \"confidence\": 0.0-1.0,\n"
        "  \"reason\": \"short reason\"\n"
        "}\n"
    )


def build_offline_merge_prompt(channel: str) -> str:
    """Run build offline merge prompt."""
    ch = str(channel or "").strip().lower()
    if ch in {"doc", OFFLINE_CHANNEL_DOC}:
        fusion = "Merge methodology/rules/checklists into one coherent protocol; keep unique safety constraints."
    elif ch in {"conv", OFFLINE_CHANNEL_CONV}:
        fusion = "Merge evolving user preferences; when direct conflict exists, prefer candidate's newer explicit rule."
    elif ch in {"traj", OFFLINE_CHANNEL_TRAJ}:
        fusion = "Keep core workflow and inject candidate's fallback/error-handling improvements where relevant."
    else:
        return ""

    return (
        "You are AutoSkill's Offline Skill Merger.\n"
        "Task: merge existing_skill and candidate_skill into ONE improved skill.\n"
        "Output ONLY strict JSON parseable by json.loads.\n\n"
        f"{fusion}\n"
        "Rules:\n"
        "- Keep the same capability identity; do not expand to unrelated tasks.\n"
        "- Perform semantic union, not raw concatenation.\n"
        "- Deduplicate triggers/tags and repeated prompt sections.\n"
        "- Keep reusable constraints; drop one-off payload details.\n"
        "- If candidate adds no durable value, keep existing mostly unchanged.\n\n"
        "Return schema fields only: {name, description, prompt, triggers, tags}.\n"
        "JSON validity: escape newlines as \\n; output raw JSON only.\n"
    )


def maybe_offline_prompt(
    *,
    channel: str,
    kind: str,
    max_candidates: Optional[int] = None,
) -> str:
    """Run maybe offline prompt."""
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
