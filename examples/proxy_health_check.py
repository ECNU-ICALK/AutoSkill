"""
AutoSkill OpenAI-compatible proxy health check and large-scale evaluation.

Usage:
  # Basic endpoint health checks (compatible with previous behavior)
  python3 -m examples.proxy_health_check --mode health --base-url http://127.0.0.1:9000

  # Large-scale extraction evaluation (assistant via proxy, optional Qwen user simulator)
  python3 -m examples.proxy_health_check \
    --mode eval \
    --base-url http://127.0.0.1:9000 \
    --eval-runs 24 \
    --report-json ./proxy_eval_report.json

  # Run both health checks and evaluation
  python3 -m examples.proxy_health_check --mode all --base-url http://127.0.0.1:9000

Optional auth:
  export AUTOSKILL_PROXY_API_KEY="your_key"
  python3 -m examples.proxy_health_check --api-key "$AUTOSKILL_PROXY_API_KEY"

Optional simulator (OpenAI-compatible endpoint, DashScope by default):
  export DASHSCOPE_API_KEY="your_dashscope_key"
  python3 -m examples.proxy_health_check --mode eval --eval-runs 30
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass
class EvalTemplate:
    template_id: str
    topic: str
    objective: str
    turns_seed: List[str]
    reuse_query: str
    expect_extract: bool
    reuse_queries: Optional[List[str]] = None
    complexity: str = "basic"


@dataclass
class EvalScenario:
    scenario_id: str
    template_id: str
    topic: str
    objective: str
    turns_seed: List[str]
    turns_final: List[str]
    reuse_query: str
    expect_extract: bool
    source: str  # template|simulator
    reuse_queries: Optional[List[str]] = None
    complexity: str = "basic"


def _short_text(text: Any, limit: int = 120) -> str:
    s = str(text or "").replace("\n", " ").strip()
    if len(s) <= int(limit):
        return s
    return s[: max(1, int(limit) - 3)] + "..."


class HTTPClient:
    def __init__(self, *, base_url: str, api_key: str, timeout_s: float) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.api_key = str(api_key or "").strip()
        self.timeout_s = float(timeout_s)

    def _headers(self, *, json_body: bool, stream: bool = False) -> Dict[str, str]:
        out: Dict[str, str] = {"Accept": ("text/event-stream" if stream else "application/json")}
        if json_body:
            out["Content-Type"] = "application/json"
        if self.api_key:
            out["Authorization"] = f"Bearer {self.api_key}"
        return out

    def request_json(
        self,
        *,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            method=str(method).upper(),
            data=data,
            headers=self._headers(json_body=(payload is not None)),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            raw = ""
            try:
                raw = e.read().decode("utf-8", errors="replace")
            except Exception:
                raw = str(e)
            raise RuntimeError(f"HTTP {e.code} {method} {path}: {raw}") from e
        except Exception as e:
            raise RuntimeError(f"Request failed {method} {path}: {e}") from e

        if not body.strip():
            return {}
        try:
            obj = json.loads(body)
        except Exception as e:
            raise RuntimeError(f"Invalid JSON from {method} {path}: {body[:500]}") from e
        if not isinstance(obj, dict):
            raise RuntimeError(f"Expected JSON object from {method} {path}, got: {type(obj).__name__}")
        return obj

    def request_stream_chat(self, *, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            method="POST",
            data=data,
            headers=self._headers(json_body=True, stream=True),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                done = False
                chunk_count = 0
                saw_data_line = False
                err_msg = ""
                content_parts: List[str] = []
                autoskill_diag: Dict[str, Any] = {}
                for raw in resp:
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    saw_data_line = True
                    payload_line = line[5:].strip()
                    if not payload_line:
                        continue
                    if payload_line == "[DONE]":
                        done = True
                        break
                    try:
                        obj = json.loads(payload_line)
                    except Exception:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    chunk_count += 1
                    if not autoskill_diag:
                        a = obj.get("autoskill")
                        if isinstance(a, dict):
                            autoskill_diag = dict(a)
                    e = obj.get("error")
                    if isinstance(e, dict):
                        msg = str(e.get("message") or "").strip()
                        if msg:
                            err_msg = msg
                    choices = obj.get("choices")
                    if isinstance(choices, list) and choices:
                        c0 = choices[0] if isinstance(choices[0], dict) else {}
                        delta = c0.get("delta")
                        if isinstance(delta, dict):
                            text = str(delta.get("content") or "")
                            if text:
                                content_parts.append(text)
                return {
                    "done": bool(done),
                    "chunk_count": int(chunk_count),
                    "saw_data_line": bool(saw_data_line),
                    "error": str(err_msg),
                    "content": "".join(content_parts).strip(),
                    "autoskill": autoskill_diag,
                }
        except urllib.error.HTTPError as e:
            raw = ""
            try:
                raw = e.read().decode("utf-8", errors="replace")
            except Exception:
                raw = str(e)
            raise RuntimeError(f"HTTP {e.code} POST {path}: {raw}") from e
        except Exception as e:
            raise RuntimeError(f"Stream request failed POST {path}: {e}") from e


class OpenAICompatLLMClient:
    """
    Lightweight OpenAI-compatible chat caller for simulator/judge models.
    """

    def __init__(self, *, base_url: str, api_key: str, model: str, timeout_s: float) -> None:
        self.http = HTTPClient(base_url=base_url, api_key=api_key, timeout_s=timeout_s)
        self.model = str(model or "").strip()
        if not self.model:
            raise ValueError("simulator model is required")

    def chat_json(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": False,
        }
        return self.http.request_json(method="POST", path="/v1/chat/completions", payload=payload)

    def chat_text(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        obj = self.chat_json(messages=messages, temperature=temperature, max_tokens=max_tokens)
        return _extract_chat_content(obj)


def _extract_chat_content(obj: Dict[str, Any]) -> str:
    choices = obj.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0] if isinstance(choices[0], dict) else {}
    msg = first.get("message")
    if isinstance(msg, dict):
        return str(msg.get("content") or "").strip()
    return ""


def _json_from_text(text: str) -> Optional[Dict[str, Any]]:
    raw = str(text or "").strip()
    if not raw:
        return None
    # Fast path: strict JSON.
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # Fallback: extract the outermost JSON object.
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        frag = raw[start : end + 1]
        try:
            obj = json.loads(frag)
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def _run_check(name: str, fn) -> CheckResult:
    try:
        detail = str(fn() or "ok")
        return CheckResult(name=name, ok=True, detail=detail)
    except Exception as e:
        return CheckResult(name=name, ok=False, detail=str(e))


def _pick_chat_model(client: HTTPClient, *, preferred: str = "") -> str:
    if str(preferred or "").strip():
        return str(preferred).strip()
    obj = client.request_json(method="GET", path="/v1/models")
    data = obj.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("models list is empty")
    first = data[0] if isinstance(data[0], dict) else {}
    model = str(first.get("id") or "").strip()
    if not model:
        raise RuntimeError("first model id is empty")
    return model


def _check_health(client: HTTPClient) -> str:
    obj = client.request_json(method="GET", path="/health")
    if not bool(obj.get("ok")):
        raise RuntimeError(f"unexpected health payload: {obj}")
    return "GET /health ok=true"


def _check_models(client: HTTPClient) -> str:
    obj = client.request_json(method="GET", path="/v1/models")
    if str(obj.get("object") or "") != "list":
        raise RuntimeError(f"unexpected object: {obj.get('object')}")
    data = obj.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("models list is empty")
    first = data[0] if isinstance(data[0], dict) else {}
    model = str(first.get("id") or "").strip() or "<empty>"
    return f"GET /v1/models count={len(data)} first={model}"


def _check_capabilities(client: HTTPClient) -> str:
    obj = client.request_json(method="GET", path="/v1/autoskill/capabilities")
    if str(obj.get("object") or "") != "autoskill.capabilities":
        raise RuntimeError(f"unexpected object: {obj.get('object')}")
    return "GET /v1/autoskill/capabilities ok"


def _proxy_chat_payload(user_id: str, *, stream: bool, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "model": str(model),
        "stream": bool(stream),
        "temperature": 0.2,
        "max_tokens": 2048,
        "user": str(user_id),
        "messages": list(messages),
    }


def _check_chat_non_stream(client: HTTPClient, *, user_id: str, model: str) -> str:
    obj = client.request_json(
        method="POST",
        path="/v1/chat/completions",
        payload=_proxy_chat_payload(
            user_id,
            stream=False,
            model=model,
            messages=[{"role": "user", "content": "Reply with one short sentence to confirm proxy health."}],
        ),
    )
    content = _extract_chat_content(obj)
    if not content:
        raise RuntimeError("assistant content is empty")
    autoskill = obj.get("autoskill")
    if not isinstance(autoskill, dict):
        raise RuntimeError("missing autoskill diagnostics")
    return f"POST /v1/chat/completions non-stream ok model={model}"


def _check_chat_stream(client: HTTPClient, *, user_id: str, model: str) -> str:
    result = client.request_stream_chat(
        path="/v1/chat/completions",
        payload=_proxy_chat_payload(
            user_id,
            stream=True,
            model=model,
            messages=[{"role": "user", "content": "Reply with one short sentence to confirm proxy health."}],
        ),
    )
    if not bool(result.get("saw_data_line")):
        raise RuntimeError("empty stream body")
    err = str(result.get("error") or "").strip()
    if err:
        raise RuntimeError(f"stream returned error chunk: {err}")
    if not bool(result.get("done")):
        raise RuntimeError("stream missing [DONE]")
    chunk_count = int(result.get("chunk_count") or 0)
    if chunk_count == 0:
        raise RuntimeError("stream has no JSON chunks")
    return f"POST /v1/chat/completions stream chunks={chunk_count} model={model}"


def _check_retrieval_preview(client: HTTPClient, *, user_id: str) -> str:
    obj = client.request_json(
        method="POST",
        path="/v1/autoskill/retrieval/preview",
        payload={
            "user": user_id,
            "messages": [{"role": "user", "content": "Please help with report writing style."}],
        },
    )
    if str(obj.get("object") or "") != "retrieval_preview":
        raise RuntimeError(f"unexpected object: {obj.get('object')}")
    hits = obj.get("hits")
    if not isinstance(hits, list):
        raise RuntimeError("retrieval hits should be a list")
    return f"POST /v1/autoskill/retrieval/preview hits={len(hits)}"


def _poll_extraction_event(
    client: HTTPClient,
    *,
    job_id: str,
    timeout_s: float,
    poll_interval_s: float = 0.6,
) -> Dict[str, Any]:
    terminal = {"completed", "failed"}
    deadline = time.time() + float(timeout_s)
    last: Dict[str, Any] = {"job_id": str(job_id), "status": "unknown"}
    while time.time() < deadline:
        try:
            obj = client.request_json(method="GET", path=f"/v1/autoskill/extractions/{job_id}")
        except Exception:
            time.sleep(float(poll_interval_s))
            continue
        cur = obj.get("data")
        if isinstance(cur, dict):
            last = cur
        status = str(last.get("status") or "").strip().lower()
        if status in terminal:
            return last
        time.sleep(float(poll_interval_s))
    return last


def _check_extraction(client: HTTPClient, *, user_id: str, timeout_s: float) -> str:
    obj = client.request_json(
        method="POST",
        path="/v1/autoskill/extractions",
        payload={
            "user": user_id,
            "messages": [
                {"role": "user", "content": "Before release: run regression, canary, monitor, full rollout."},
                {"role": "assistant", "content": "Understood, I will follow this process."},
            ],
            "hint": "extract release-process skill",
        },
    )
    data = obj.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"unexpected extraction payload: {obj}")
    job_id = str(data.get("job_id") or "").strip()
    if not job_id:
        raise RuntimeError("missing extraction job_id")
    final_event = _poll_extraction_event(client, job_id=job_id, timeout_s=timeout_s)
    status = str(final_event.get("status") or "unknown")
    upserted = final_event.get("upserted")
    count = len(upserted) if isinstance(upserted, list) else 0
    return f"extraction status={status} upserted={count}"


def _check_embeddings(client: HTTPClient) -> str:
    obj = client.request_json(
        method="POST",
        path="/v1/embeddings",
        payload={"input": "AutoSkill proxy embedding health check."},
    )
    data = obj.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("embedding data is empty")
    emb = data[0].get("embedding") if isinstance(data[0], dict) else None
    if not isinstance(emb, list) or not emb:
        raise RuntimeError("embedding vector is empty")
    return f"POST /v1/embeddings dims={len(emb)}"


def run_health_checks(
    *,
    client: HTTPClient,
    user_id: str,
    model: str,
    timeout_s: float,
    skip_embeddings: bool,
) -> Tuple[List[CheckResult], bool]:
    model_cache: Dict[str, str] = {"id": str(model or "").strip()}

    def _resolve_model() -> str:
        mid = str(model_cache.get("id") or "").strip()
        if mid:
            return mid
        mid = _pick_chat_model(client, preferred="")
        model_cache["id"] = mid
        return mid

    checks = [
        ("health", lambda: _check_health(client)),
        ("models", lambda: _check_models(client)),
        ("capabilities", lambda: _check_capabilities(client)),
        ("chat_non_stream", lambda: _check_chat_non_stream(client, user_id=user_id, model=_resolve_model())),
        ("chat_stream", lambda: _check_chat_stream(client, user_id=user_id, model=_resolve_model())),
        ("retrieval_preview", lambda: _check_retrieval_preview(client, user_id=user_id)),
        ("extraction", lambda: _check_extraction(client, user_id=user_id, timeout_s=timeout_s)),
    ]
    if not bool(skip_embeddings):
        checks.append(("embeddings", lambda: _check_embeddings(client)))

    results = [_run_check(name, fn) for name, fn in checks]
    ok_count = sum(1 for r in results if r.ok)
    total = len(results)
    all_ok = (ok_count == total)
    return results, all_ok


def _build_eval_templates() -> List[EvalTemplate]:
    return [
        EvalTemplate(
            template_id="skill_switch_policy_to_social",
            topic="topic switch: policy report to social post",
            objective=(
                "In one dialogue, the user first requests a formal policy report and then switches to a "
                "public-facing social post with different completion criteria."
            ),
            turns_seed=[
                "Draft a formal government report on autonomous AI operations risk management.",
                "Use formal Word-style prose, no tables, no fancy symbols, and avoid hallucinations.",
                "Make it concrete with accountability, measurable indicators, and sharp problem framing.",
                "Now switch task: rewrite the same core ideas as a public WeChat-style article for general readers.",
                "Use a readable and engaging tone, but still no tables and no fabricated facts.",
                "Add a strong title and a short 3-part structure with section headings.",
                "Keep arguments evidence-oriented and easy to follow.",
            ],
            reuse_query="Write a WeChat-style explainer article on AI governance with a strong title and no tables.",
            reuse_queries=[
                "Write a formal policy report on AI governance with strict official style and no tables.",
                "Write a WeChat-style explainer article on AI governance with a strong title and no tables.",
            ],
            expect_extract=True,
            complexity="complex_switch",
        ),
        EvalTemplate(
            template_id="long_incident_playbook_updates",
            topic="long multi-turn incident response playbook",
            objective=(
                "Stress test long conversations where the user repeatedly updates constraints and expects "
                "a reusable incident response workflow."
            ),
            turns_seed=[
                "Create an incident response playbook for an online service outage.",
                "Include severity levels and clear owner responsibilities.",
                "Add a communication timeline for internal and external updates.",
                "Avoid blame language and keep the tone factual.",
                "Add rollback and mitigation checkpoints with explicit go/no-go criteria.",
                "Make escalation rules stricter for repeated failures within 24 hours.",
                "Add a post-incident review template focused on action items, not narration.",
                "Now compress the playbook into a concise version for on-call engineers.",
                "Final revision: remove ambiguity and enforce measurable completion criteria.",
            ],
            reuse_query="Generate a concise outage incident playbook with severity, escalation, and measurable checkpoints.",
            reuse_queries=[
                "Generate a detailed outage incident playbook with communication timelines and escalation rules.",
                "Generate a concise on-call incident playbook with measurable go/no-go checkpoints.",
            ],
            expect_extract=True,
            complexity="complex_long",
        ),
        EvalTemplate(
            template_id="customer_support_triage_workflow",
            topic="customer support triage and escalation",
            objective=(
                "Evaluate extraction for operations workflows beyond coding and writing style tasks."
            ),
            turns_seed=[
                "Design a support ticket triage process for a SaaS customer support team.",
                "Prioritize by business impact and urgency, not only by first-come-first-served.",
                "Add clear escalation triggers and handoff conditions to engineering.",
                "Use a calm, professional tone for customer-facing templates.",
                "Add a quality check to reduce repetitive back-and-forth with customers.",
                "Refine the process for weekends with reduced staffing.",
            ],
            reuse_query="Create a SaaS support triage flow with impact-based priority and clear escalation triggers.",
            expect_extract=True,
            complexity="complex_domain",
        ),
        EvalTemplate(
            template_id="research_interview_protocol_refinement",
            topic="user research interview protocol",
            objective=(
                "Capture reusable interview planning preferences with iterative updates."
            ),
            turns_seed=[
                "Help me build a user interview protocol for a new analytics dashboard.",
                "Focus on behavior-based questions instead of opinion-only questions.",
                "Add a consent script and avoid leading questions.",
                "Add a scoring rubric for prioritizing recurring pain points.",
                "Now shorten it for a 20-minute remote interview slot.",
            ],
            reuse_query="Create a concise user interview protocol with behavior-based questions and a pain-point rubric.",
            expect_extract=True,
            complexity="complex_domain",
        ),
        EvalTemplate(
            template_id="workshop_facilitation_agenda",
            topic="cross-team workshop facilitation",
            objective=(
                "Test reusable facilitation skill extraction with concrete constraints."
            ),
            turns_seed=[
                "Design a 90-minute cross-team alignment workshop agenda.",
                "We need clear decisions, not brainstorming without closure.",
                "Include time-boxed segments and decision checkpoints.",
                "Add fallback plans if discussion diverges.",
                "Provide facilitator prompts that keep discussion objective.",
            ],
            reuse_query="Build a time-boxed workshop agenda with decision checkpoints and facilitator prompts.",
            expect_extract=True,
            complexity="complex_domain",
        ),
        EvalTemplate(
            template_id="gov_report_style",
            topic="government report writing",
            objective="Write a policy report with strict formal constraints and strong viewpoints.",
            turns_seed=[
                "Write a government report about self-evolving large-model systems.",
                "Use formal Word-style prose, no table, no fancy symbols, and avoid hallucinations.",
                "Make it more concrete and critical, with clear problem statements and independent insights.",
            ],
            reuse_query="Write another government report with formal style, no table, and critical analysis.",
            expect_extract=True,
            complexity="basic",
        ),
        EvalTemplate(
            template_id="code_generation_preferences",
            topic="code generation preferences",
            objective="Generate implementation following stable user coding preferences.",
            turns_seed=[
                "Implement a high-performance log parser for large files.",
                "Do not use Python. Use C, and keep code comments concise and practical.",
                "Only annotate important functions, and output code directly.",
            ],
            reuse_query="Generate C code with concise function-level comments and no extra narrative.",
            expect_extract=True,
            complexity="basic",
        ),
        EvalTemplate(
            template_id="email_personalization",
            topic="personalized email drafting",
            objective="Draft emails that follow user-specific tone and structure preferences.",
            turns_seed=[
                "Help me draft an outreach email for a collaboration invitation.",
                "Keep it concise, polite, and avoid over-selling language.",
                "Add a concrete CTA and a clear subject line; keep the body under 120 words.",
            ],
            reuse_query="Draft a concise collaboration email with polite tone and concrete CTA.",
            expect_extract=True,
            complexity="basic",
        ),
        EvalTemplate(
            template_id="summary_format_control",
            topic="structured summary style",
            objective="Produce summaries under stable formatting constraints.",
            turns_seed=[
                "Summarize this technical proposal for leadership.",
                "No bullet tables. Use short sections and explicit risks/next actions.",
                "Keep style plain and avoid decorative language.",
            ],
            reuse_query="Summarize a technical proposal with explicit risks and actions, no tables.",
            expect_extract=True,
            complexity="basic",
        ),
        EvalTemplate(
            template_id="one_off_fact_question",
            topic="one-off factual QA",
            objective="Simple one-shot factual request without durable workflow preference.",
            turns_seed=[
                "What is the difference between TCP and UDP?",
            ],
            reuse_query="Explain TCP vs UDP briefly.",
            expect_extract=False,
            complexity="basic_negative",
        ),
        EvalTemplate(
            template_id="single_translation",
            topic="single translation",
            objective="One-time translation request without persistent user preference.",
            turns_seed=[
                "Translate this sentence to English: 该系统支持在线增量更新。",
            ],
            reuse_query="Translate: 模型会持续学习并更新技能。",
            expect_extract=False,
            complexity="basic_negative",
        ),
        EvalTemplate(
            template_id="casual_multi_turn_chat",
            topic="casual multi-turn chat",
            objective="Multi-turn casual dialogue without stable reusable capability signal.",
            turns_seed=[
                "How was your day?",
                "Tell me one interesting fact about rainbows.",
                "Nice. Also recommend a movie for tonight.",
                "Thanks, that is all.",
            ],
            reuse_query="Suggest a movie for tonight.",
            expect_extract=False,
            complexity="complex_negative",
        ),
    ]


def _simulate_turns_with_llm(
    *,
    sim_llm: OpenAICompatLLMClient,
    template: EvalTemplate,
    target_turns: int,
) -> Optional[List[str]]:
    system = (
        "You are a user-turn generator for benchmark conversations.\n"
        "Return strict JSON only: {\"turns\":[\"...\", ...]}.\n"
        "Rules:\n"
        "- Keep coherent progression; if seed turns include an explicit topic switch, keep that switch.\n"
        "- Make turns natural and concise.\n"
        "- Preserve the original objective and constraints.\n"
        "- Do not output assistant text.\n"
    )
    payload = {
        "topic": template.topic,
        "objective": template.objective,
        "complexity": template.complexity,
        "seed_turns": list(template.turns_seed),
        "reuse_queries": list(template.reuse_queries or []),
        "target_turns": int(target_turns),
    }
    user = (
        "Generate benchmark user turns.\n"
        f"DATA:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    out = sim_llm.chat_text(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=1200,
    )
    parsed = _json_from_text(out)
    if not isinstance(parsed, dict):
        return None
    turns = parsed.get("turns")
    if not isinstance(turns, list):
        return None
    cleaned = [str(x).strip() for x in turns if str(x).strip()]
    if len(cleaned) < 1:
        return None
    return cleaned[: max(1, int(target_turns))]


def _sample_scenarios(
    *,
    runs: int,
    seed: int,
    simulator: Optional[OpenAICompatLLMClient],
    verbose: bool,
) -> List[EvalScenario]:
    templates = _build_eval_templates()
    if not templates:
        return []
    rng = random.Random(int(seed))
    out: List[EvalScenario] = []
    for i in range(max(1, int(runs))):
        t = templates[i % len(templates)]
        scenario_id = f"case_{i + 1:03d}_{t.template_id}"
        turns_seed = list(t.turns_seed)
        # Keep slight variation while preserving semantics.
        if len(turns_seed) >= 2 and rng.random() < 0.35:
            turns_seed[-1] = f"{turns_seed[-1]} Also keep it concise."
        final_turns = list(turns_seed)
        source = "template"
        if simulator is not None:
            try:
                sim_turns = _simulate_turns_with_llm(
                    sim_llm=simulator, template=t, target_turns=len(turns_seed)
                )
            except Exception:
                sim_turns = None
            if sim_turns:
                final_turns = list(sim_turns)
                source = "simulator"
        if verbose:
            print(
                f"[eval] scenario={scenario_id} source={source} complexity={t.complexity} "
                f"turns={len(final_turns)}"
            )
        out.append(
            EvalScenario(
                scenario_id=scenario_id,
                template_id=t.template_id,
                topic=t.topic,
                objective=t.objective,
                turns_seed=turns_seed,
                turns_final=final_turns,
                reuse_query=t.reuse_query,
                expect_extract=bool(t.expect_extract),
                source=source,
                reuse_queries=list(t.reuse_queries or []),
                complexity=str(t.complexity or "basic"),
            )
        )
    return out


def _judge_skill_with_llm(
    *,
    judge_llm: OpenAICompatLLMClient,
    scenario: EvalScenario,
    skill: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    system = (
        "You are an evaluator for AutoSkill extraction quality.\n"
        "Return strict JSON only:\n"
        "{\"pass\": true|false, \"score\": 1-5, \"reason\": \"...\"}\n"
        "Judge whether the skill is reusable, user-centric, and not polluted by one-off task specifics."
    )
    user = (
        "SCENARIO:\n"
        f"{json.dumps({'topic': scenario.topic, 'objective': scenario.objective, 'turns': scenario.turns_final}, ensure_ascii=False)}\n"
        "SKILL:\n"
        f"{json.dumps(skill, ensure_ascii=False)}"
    )
    out = judge_llm.chat_text(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.0,
        max_tokens=512,
    )
    parsed = _json_from_text(out)
    if not isinstance(parsed, dict):
        return None
    score_raw = parsed.get("score")
    try:
        score = int(score_raw)
    except Exception:
        score = 0
    return {
        "pass": bool(parsed.get("pass")),
        "score": max(0, min(5, score)),
        "reason": str(parsed.get("reason") or "").strip(),
    }


def _run_eval_case(
    *,
    client: HTTPClient,
    model: str,
    scenario: EvalScenario,
    user_prefix: str,
    chat_stream: bool,
    turn_timeout_s: float,
    extraction_timeout_s: float,
    poll_interval_s: float,
    judge_llm: Optional[OpenAICompatLLMClient],
    verbose: bool,
) -> Dict[str, Any]:
    user_id = f"{user_prefix}_{scenario.scenario_id}"
    messages: List[Dict[str, str]] = []
    turns: List[Dict[str, Any]] = []
    job_ids: List[str] = []
    case_start = time.time()

    print(
        f"[eval][case] start id={scenario.scenario_id} topic={scenario.topic} "
        f"expect_extract={int(bool(scenario.expect_extract))} source={scenario.source} "
        f"complexity={scenario.complexity}"
    )

    # 1) Run scenario conversation against proxy assistant (InternLM backend).
    for idx, user_turn in enumerate(scenario.turns_final, start=1):
        turn_user = str(user_turn or "").strip()
        if not turn_user:
            continue
        if verbose:
            print(
                f"[eval][turn] case={scenario.scenario_id} idx={idx} "
                f"user={_short_text(turn_user, 180)}"
            )
        messages.append({"role": "user", "content": turn_user})
        payload = _proxy_chat_payload(
            user_id=user_id,
            stream=bool(chat_stream),
            model=model,
            messages=messages,
        )

        assistant_text = ""
        autoskill: Dict[str, Any] = {}
        if bool(chat_stream):
            prev_timeout = client.timeout_s
            client.timeout_s = float(turn_timeout_s)
            try:
                stream_obj = client.request_stream_chat(path="/v1/chat/completions", payload=payload)
            except Exception as e:
                raise RuntimeError(
                    f"chat_stream_failed turn={idx} user={_short_text(turn_user, 120)} err={e}"
                ) from e
            finally:
                client.timeout_s = prev_timeout
            err = str(stream_obj.get("error") or "").strip()
            if err:
                raise RuntimeError(f"stream turn {idx} error: {err}")
            assistant_text = str(stream_obj.get("content") or "").strip()
            autoskill_raw = stream_obj.get("autoskill")
            autoskill = dict(autoskill_raw) if isinstance(autoskill_raw, dict) else {}
        else:
            prev_timeout = client.timeout_s
            client.timeout_s = float(turn_timeout_s)
            try:
                obj = client.request_json(method="POST", path="/v1/chat/completions", payload=payload)
            except Exception as e:
                raise RuntimeError(
                    f"chat_non_stream_failed turn={idx} user={_short_text(turn_user, 120)} err={e}"
                ) from e
            finally:
                client.timeout_s = prev_timeout
            assistant_text = _extract_chat_content(obj)
            autoskill_raw = obj.get("autoskill")
            autoskill = dict(autoskill_raw) if isinstance(autoskill_raw, dict) else {}

        if not assistant_text:
            assistant_text = "(empty response)"
        messages.append({"role": "assistant", "content": assistant_text})

        extraction_diag = autoskill.get("extraction")
        extraction_job_id = ""
        extraction_status = "unknown"
        if isinstance(extraction_diag, dict):
            extraction_job_id = str(extraction_diag.get("job_id") or "").strip()
            extraction_status = str(extraction_diag.get("status") or "unknown").strip().lower()
        if extraction_job_id and extraction_job_id not in job_ids:
            job_ids.append(extraction_job_id)

        retrieval_diag = autoskill.get("retrieval")
        retrieval_obj = dict(retrieval_diag) if isinstance(retrieval_diag, dict) else {}
        if verbose:
            hit_count = len(list(retrieval_obj.get("hits") or []))
            selected_ids = list(retrieval_obj.get("selected_for_context_ids") or [])
            print(
                f"[eval][turn] case={scenario.scenario_id} idx={idx} "
                f"assistant_len={len(assistant_text)} retrieval_hits={hit_count} "
                f"selected={len(selected_ids)} extract_status={extraction_status} "
                f"job_id={extraction_job_id or '-'}"
            )

        turns.append(
            {
                "turn_index": int(idx),
                "user": turn_user,
                "assistant": assistant_text,
                "autoskill": {
                    "retrieval": retrieval_obj,
                    "extraction": {
                        "job_id": extraction_job_id or None,
                        "status": extraction_status,
                    },
                },
            }
        )

    # 2) Poll extraction jobs until terminal.
    events_by_job: Dict[str, Dict[str, Any]] = {}
    if not job_ids:
        print(f"[eval][extract] case={scenario.scenario_id} no_job_ids")
    for jid in job_ids:
        if verbose:
            print(f"[eval][extract] case={scenario.scenario_id} poll job_id={jid}")
        ev = _poll_extraction_event(
            client,
            job_id=jid,
            timeout_s=float(extraction_timeout_s),
            poll_interval_s=float(poll_interval_s),
        )
        events_by_job[jid] = ev
        st = str(ev.get("status") or "unknown").strip().lower()
        ups = ev.get("upserted")
        ups_n = len(ups) if isinstance(ups, list) else 0
        err = _short_text(ev.get("error") or "", 160)
        print(
            f"[eval][extract] case={scenario.scenario_id} job_id={jid} "
            f"status={st} upserted={ups_n}" + (f" error={err}" if err else "")
        )

    events = list(events_by_job.values())
    completed = [e for e in events if str(e.get("status") or "").strip().lower() == "completed"]
    failed = [e for e in events if str(e.get("status") or "").strip().lower() == "failed"]
    upserted_total = 0
    extracted_skill_ids: List[str] = []
    extracted_skill_details: List[Dict[str, Any]] = []
    for ev in completed:
        ups = ev.get("upserted")
        if isinstance(ups, list):
            upserted_total += len(ups)
            for it in ups:
                if isinstance(it, dict):
                    sid = str(it.get("id") or "").strip()
                    if sid and sid not in extracted_skill_ids:
                        extracted_skill_ids.append(sid)
        skills = ev.get("skills")
        if isinstance(skills, list):
            for s in skills:
                if isinstance(s, dict):
                    extracted_skill_details.append(dict(s))

    extracted = (upserted_total > 0)

    # 3) Retrieval reuse checks after extraction (single or multi-query).
    reuse_queries: List[str] = []
    for q in list(scenario.reuse_queries or []):
        qs = str(q or "").strip()
        if qs:
            reuse_queries.append(qs)
    q_primary = str(scenario.reuse_query or "").strip()
    if q_primary and q_primary not in reuse_queries:
        reuse_queries.append(q_primary)
    if not reuse_queries:
        reuse_queries.append(str(scenario.reuse_query or ""))

    reuse_checks: List[Dict[str, Any]] = []
    for q_idx, q in enumerate(reuse_queries, start=1):
        try:
            reuse = client.request_json(
                method="POST",
                path="/v1/autoskill/retrieval/preview",
                payload={
                    "user": user_id,
                    "query": q,
                },
            )
        except Exception as e:
            raise RuntimeError(
                f"reuse_retrieval_failed query_idx={q_idx} query={_short_text(q, 120)} err={e}"
            ) from e

        hits = reuse.get("hits")
        if not isinstance(hits, list):
            hits = []
        selected_ids = reuse.get("selected_for_context_ids")
        if not isinstance(selected_ids, list):
            selected_ids = []
        reuse_top = hits[0] if hits and isinstance(hits[0], dict) else {}
        reuse_pass_i = bool(selected_ids)
        top_name = str((reuse_top or {}).get("name") or "").strip()
        top_score = (reuse_top or {}).get("score")
        print(
            f"[eval][reuse] case={scenario.scenario_id} q={q_idx}/{len(reuse_queries)} "
            f"pass={int(bool(reuse_pass_i))} hits={len(hits)} selected={len(selected_ids)} "
            f"top={_short_text(top_name, 80) or '-'} score={top_score}"
        )
        reuse_checks.append(
            {
                "query": q,
                "selected_for_context_ids": list(selected_ids),
                "hit_count": len(hits),
                "top_hit": dict(reuse_top) if isinstance(reuse_top, dict) else {},
                "pass": bool(reuse_pass_i),
            }
        )

    retrieval_reuse_pass = any(bool(x.get("pass")) for x in reuse_checks)
    reuse_primary = reuse_checks[0] if reuse_checks else {
        "query": q_primary,
        "selected_for_context_ids": [],
        "hit_count": 0,
        "top_hit": {},
        "pass": False,
    }

    # 4) Optional LLM judge for extracted skill quality.
    judge = None
    if judge_llm is not None and extracted_skill_details:
        try:
            judge = _judge_skill_with_llm(
                judge_llm=judge_llm,
                scenario=scenario,
                skill=extracted_skill_details[0],
            )
            if isinstance(judge, dict):
                print(
                    f"[eval][judge] case={scenario.scenario_id} pass={int(bool(judge.get('pass')))} "
                    f"score={judge.get('score')} reason={_short_text(judge.get('reason'), 120)}"
                )
        except Exception:
            judge = None

    expect_extract = bool(scenario.expect_extract)
    tp = int(expect_extract and extracted)
    fn = int(expect_extract and (not extracted))
    fp = int((not expect_extract) and extracted)
    tn = int((not expect_extract) and (not extracted))
    case_elapsed = time.time() - case_start
    print(
        f"[eval][case] done id={scenario.scenario_id} elapsed_s={case_elapsed:.2f} "
        f"extracted={int(bool(extracted))} upserted={upserted_total} "
        f"expect_extract={int(expect_extract)} reuse_pass={int(bool(retrieval_reuse_pass))} "
        f"reuse_pass_count={sum(1 for x in reuse_checks if bool(x.get('pass')))}"
    )

    return {
        "scenario": {
            "id": scenario.scenario_id,
            "template_id": scenario.template_id,
            "topic": scenario.topic,
            "objective": scenario.objective,
            "expect_extract": expect_extract,
            "source": scenario.source,
            "complexity": scenario.complexity,
            "turns_seed": list(scenario.turns_seed),
            "turns_final": list(scenario.turns_final),
            "reuse_query": scenario.reuse_query,
            "reuse_queries": list(scenario.reuse_queries or []),
        },
        "user_id": user_id,
        "turns": turns,
        "extraction": {
            "job_ids": list(job_ids),
            "events_by_job": events_by_job,
            "completed_jobs": len(completed),
            "failed_jobs": len(failed),
            "upserted_total": int(upserted_total),
            "extracted": bool(extracted),
            "skill_ids": extracted_skill_ids,
            "skills": extracted_skill_details,
        },
        "reuse_retrieval": {
            "query": str(reuse_primary.get("query") or scenario.reuse_query),
            "selected_for_context_ids": list(reuse_primary.get("selected_for_context_ids") or []),
            "hit_count": int(reuse_primary.get("hit_count") or 0),
            "top_hit": dict(reuse_primary.get("top_hit") or {}),
            "pass": bool(retrieval_reuse_pass),
            "checks": reuse_checks,
            "pass_count": sum(1 for x in reuse_checks if bool(x.get("pass"))),
        },
        "judge": judge,
        "confusion": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
    }


def run_eval(
    *,
    client: HTTPClient,
    model: str,
    eval_runs: int,
    eval_seed: int,
    user_prefix: str,
    eval_stream: bool,
    turn_timeout_s: float,
    extraction_timeout_s: float,
    poll_interval_s: float,
    simulator: Optional[OpenAICompatLLMClient],
    judge_llm: Optional[OpenAICompatLLMClient],
    verbose: bool,
) -> Dict[str, Any]:
    scenarios = _sample_scenarios(
        runs=eval_runs,
        seed=eval_seed,
        simulator=simulator,
        verbose=verbose,
    )
    cases: List[Dict[str, Any]] = []
    start_ts = time.time()

    for i, sc in enumerate(scenarios, start=1):
        print(
            f"[eval] running {i}/{len(scenarios)} id={sc.scenario_id} "
            f"template={sc.template_id} source={sc.source} complexity={sc.complexity}"
        )
        try:
            case = _run_eval_case(
                client=client,
                model=model,
                scenario=sc,
                user_prefix=user_prefix,
                chat_stream=eval_stream,
                turn_timeout_s=turn_timeout_s,
                extraction_timeout_s=extraction_timeout_s,
                poll_interval_s=poll_interval_s,
                judge_llm=judge_llm,
                verbose=verbose,
            )
            case["ok"] = True
            case["error"] = ""
            ext = case.get("extraction") if isinstance(case, dict) else {}
            rr = case.get("reuse_retrieval") if isinstance(case, dict) else {}
            print(
                f"[eval] pass id={sc.scenario_id} upserted={int((ext or {}).get('upserted_total') or 0)} "
                f"extracted={int(bool((ext or {}).get('extracted')))} "
                f"reuse_pass={int(bool((rr or {}).get('pass')))}"
            )
        except Exception as e:
            err_text = str(e)
            tb = traceback.format_exc(limit=5)
            print(f"[eval] FAIL id={sc.scenario_id}: {err_text}")
            print(
                f"[eval] context id={sc.scenario_id} "
                f"topic={sc.topic} objective={_short_text(sc.objective, 180)}"
            )
            if sc.turns_final:
                print(
                    f"[eval] last_user_turn id={sc.scenario_id} "
                    f"text={_short_text(sc.turns_final[-1], 220)}"
                )
            if verbose:
                print(f"[eval] traceback id={sc.scenario_id}:\n{tb}")
            case = {
                "scenario": {
                    "id": sc.scenario_id,
                    "template_id": sc.template_id,
                    "topic": sc.topic,
                    "objective": sc.objective,
                    "expect_extract": bool(sc.expect_extract),
                    "source": sc.source,
                    "complexity": sc.complexity,
                    "turns_seed": list(sc.turns_seed),
                    "turns_final": list(sc.turns_final),
                    "reuse_query": sc.reuse_query,
                    "reuse_queries": list(sc.reuse_queries or []),
                },
                "ok": False,
                "error": err_text,
                "traceback": tb,
            }
        cases.append(case)

    elapsed_s = float(time.time() - start_ts)

    tp = fn = fp = tn = 0
    completed_jobs = failed_jobs = upserted_total = 0
    reuse_pass = 0
    extracted_count = 0
    ok_cases = 0
    judge_scores: List[int] = []
    for c in cases:
        if bool(c.get("ok")):
            ok_cases += 1
            conf = c.get("confusion")
            if isinstance(conf, dict):
                tp += int(conf.get("tp") or 0)
                fn += int(conf.get("fn") or 0)
                fp += int(conf.get("fp") or 0)
                tn += int(conf.get("tn") or 0)
            ext = c.get("extraction")
            if isinstance(ext, dict):
                completed_jobs += int(ext.get("completed_jobs") or 0)
                failed_jobs += int(ext.get("failed_jobs") or 0)
                upserted_total += int(ext.get("upserted_total") or 0)
                if bool(ext.get("extracted")):
                    extracted_count += 1
            rr = c.get("reuse_retrieval")
            if isinstance(rr, dict) and bool(rr.get("pass")):
                reuse_pass += 1
            j = c.get("judge")
            if isinstance(j, dict):
                try:
                    judge_scores.append(int(j.get("score") or 0))
                except Exception:
                    pass

    total_cases = len(cases)
    template_counts: Dict[str, int] = {}
    complexity_counts: Dict[str, int] = {}
    for c in cases:
        sc = c.get("scenario") if isinstance(c, dict) else {}
        if isinstance(sc, dict):
            tid = str(sc.get("template_id") or "").strip()
            if tid:
                template_counts[tid] = int(template_counts.get(tid, 0)) + 1
            comp = str(sc.get("complexity") or "basic").strip() or "basic"
            complexity_counts[comp] = int(complexity_counts.get(comp, 0)) + 1
    expected_positive = tp + fn
    expected_negative = fp + tn
    extraction_recall = (float(tp) / expected_positive) if expected_positive > 0 else None
    extraction_fp_rate = (float(fp) / expected_negative) if expected_negative > 0 else None
    reuse_pass_rate = (float(reuse_pass) / max(1, ok_cases))
    avg_judge_score = (sum(judge_scores) / len(judge_scores)) if judge_scores else None

    summary = {
        "total_cases": total_cases,
        "ok_cases": ok_cases,
        "failed_cases": total_cases - ok_cases,
        "elapsed_s": elapsed_s,
        "jobs": {
            "completed": completed_jobs,
            "failed": failed_jobs,
            "upserted_total": upserted_total,
        },
        "confusion": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
        "metrics": {
            "extraction_recall_on_expected": extraction_recall,
            "false_positive_rate_on_unexpected": extraction_fp_rate,
            "case_level_extracted_rate": (float(extracted_count) / max(1, ok_cases)),
            "retrieval_reuse_pass_rate": reuse_pass_rate,
            "avg_judge_score": avg_judge_score,
        },
        "coverage": {
            "templates": template_counts,
            "complexity": complexity_counts,
        },
    }
    return {"summary": summary, "cases": cases}


def _build_simulator_client(
    *,
    sim_enabled: bool,
    sim_base_url: str,
    sim_api_key: str,
    sim_model: str,
    timeout_s: float,
) -> Optional[OpenAICompatLLMClient]:
    if not bool(sim_enabled):
        return None
    if not str(sim_api_key or "").strip():
        return None
    try:
        return OpenAICompatLLMClient(
            base_url=str(sim_base_url),
            api_key=str(sim_api_key),
            model=str(sim_model),
            timeout_s=float(timeout_s),
        )
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Health-check and evaluate AutoSkill proxy")
    parser.add_argument("--mode", default="health", choices=["health", "eval", "all"])
    parser.add_argument("--base-url", default="http://127.0.0.1:9000")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--user-id", default="proxy_test_user")
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout-s", type=float, default=25.0)
    parser.add_argument("--skip-embeddings", action="store_true")

    parser.add_argument("--eval-runs", type=int, default=24)
    parser.add_argument("--eval-seed", type=int, default=42)
    parser.add_argument("--eval-user-prefix", default="proxy_eval")
    parser.add_argument("--eval-stream", action="store_true")
    parser.add_argument("--eval-turn-timeout-s", type=float, default=120.0)
    parser.add_argument("--eval-extraction-timeout-s", type=float, default=180.0)
    parser.add_argument("--eval-poll-interval-s", type=float, default=0.8)
    parser.add_argument("--strict-eval", action="store_true")
    parser.add_argument("--min-recall", type=float, default=0.5)
    parser.add_argument("--max-fp-rate", type=float, default=0.5)

    parser.add_argument("--sim-disable", action="store_true")
    parser.add_argument(
        "--sim-base-url",
        default=os.getenv("EVAL_SIM_BASE_URL", os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode")),
    )
    parser.add_argument(
        "--sim-api-key",
        default=os.getenv("EVAL_SIM_API_KEY", os.getenv("DASHSCOPE_API_KEY", "")),
    )
    parser.add_argument("--sim-model", default=os.getenv("EVAL_SIM_MODEL", "qwen-plus"))
    parser.add_argument("--judge-enable", action="store_true")
    parser.add_argument("--report-json", default="")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print turn-level progress and traceback details for evaluation cases.",
    )
    args = parser.parse_args()

    client = HTTPClient(
        base_url=str(args.base_url),
        api_key=str(args.api_key),
        timeout_s=float(args.timeout_s),
    )

    model = str(args.model or "").strip()
    report: Dict[str, Any] = {
        "meta": {
            "base_url": str(args.base_url),
            "mode": str(args.mode),
            "model": str(model),
            "time_unix": int(time.time()),
        }
    }

    overall_ok = True

    if args.mode in {"health", "all"}:
        results, all_ok = run_health_checks(
            client=client,
            user_id=str(args.user_id),
            model=str(model),
            timeout_s=float(args.timeout_s),
            skip_embeddings=bool(args.skip_embeddings),
        )
        report["health"] = {
            "ok": bool(all_ok),
            "results": [{"name": r.name, "ok": r.ok, "detail": r.detail} for r in results],
        }
        for r in results:
            tag = "PASS" if r.ok else "FAIL"
            print(f"[{tag}] {r.name}: {r.detail}")
        if all_ok:
            print(f"\nHealth checks passed ({sum(1 for r in results if r.ok)}/{len(results)}).")
        else:
            print(f"\nHealth checks failed ({sum(1 for r in results if r.ok)}/{len(results)} passed).")
            overall_ok = False

    if args.mode in {"eval", "all"}:
        if not model:
            try:
                model = _pick_chat_model(client, preferred="")
            except Exception as e:
                print(
                    "[eval] cannot discover model from proxy. "
                    "Please ensure proxy is running and reachable."
                )
                print(f"[eval] discovery error: {e}")
                overall_ok = False
                if args.mode == "eval":
                    raise SystemExit(1)

        sim_enabled = not bool(args.sim_disable)
        simulator = _build_simulator_client(
            sim_enabled=sim_enabled,
            sim_base_url=str(args.sim_base_url),
            sim_api_key=str(args.sim_api_key),
            sim_model=str(args.sim_model),
            timeout_s=float(args.timeout_s),
        )
        judge_llm = simulator if bool(args.judge_enable) else None

        if simulator is None:
            print("[eval] simulator: disabled (using template turns)")
        else:
            print(f"[eval] simulator: enabled model={args.sim_model}")
        if judge_llm is not None:
            print(f"[eval] judge: enabled model={args.sim_model}")

        eval_result = run_eval(
            client=client,
            model=model,
            eval_runs=int(args.eval_runs),
            eval_seed=int(args.eval_seed),
            user_prefix=str(args.eval_user_prefix),
            eval_stream=bool(args.eval_stream),
            turn_timeout_s=float(args.eval_turn_timeout_s),
            extraction_timeout_s=float(args.eval_extraction_timeout_s),
            poll_interval_s=float(args.eval_poll_interval_s),
            simulator=simulator,
            judge_llm=judge_llm,
            verbose=bool(args.verbose),
        )
        report["evaluation"] = eval_result

        summary = eval_result.get("summary") if isinstance(eval_result, dict) else {}
        metrics = summary.get("metrics") if isinstance(summary, dict) else {}
        conf = summary.get("confusion") if isinstance(summary, dict) else {}
        coverage = summary.get("coverage") if isinstance(summary, dict) else {}
        total_cases = int(summary.get("total_cases") or 0)
        ok_cases = int(summary.get("ok_cases") or 0)
        recall = metrics.get("extraction_recall_on_expected")
        fp_rate = metrics.get("false_positive_rate_on_unexpected")
        reuse_pass_rate = metrics.get("retrieval_reuse_pass_rate")

        print("\n[eval] summary:")
        print(
            json.dumps(
                {
                    "total_cases": total_cases,
                    "ok_cases": ok_cases,
                    "confusion": conf,
                    "metrics": metrics,
                    "coverage": coverage,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        if bool(args.strict_eval):
            strict_ok = True
            if isinstance(recall, (int, float)) and float(recall) < float(args.min_recall):
                strict_ok = False
                print(
                    f"[eval][strict] recall too low: {float(recall):.3f} < {float(args.min_recall):.3f}"
                )
            if isinstance(fp_rate, (int, float)) and float(fp_rate) > float(args.max_fp_rate):
                strict_ok = False
                print(
                    f"[eval][strict] fp_rate too high: {float(fp_rate):.3f} > {float(args.max_fp_rate):.3f}"
                )
            if not strict_ok:
                overall_ok = False
            else:
                print(
                    f"[eval][strict] passed (recall={recall}, fp_rate={fp_rate}, reuse_pass_rate={reuse_pass_rate})"
                )

    report_path = str(args.report_json or "").strip()
    if report_path:
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\nReport saved: {report_path}")
        except Exception as e:
            print(f"\nFailed to save report to {report_path}: {e}")
            overall_ok = False

    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
