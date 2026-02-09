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


def _has_cjk(text: Any) -> bool:
    s = str(text or "")
    return any(("\u4e00" <= ch <= "\u9fff") for ch in s)


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
    variants_pos_zh: List[Tuple[str, str, str]] = [
        ("budget", "预算再压缩10%，给不降核心质量的替代方案。", "并附预算压缩版替代方案。"),
        ("timeline", "把时间压缩一周，说明哪些步骤不能删。", "并附时间压缩一周的执行版本。"),
        ("roles", "明确家庭成员/参与者分工和交接节点。", "并附角色分工与交接清单。"),
        ("risk", "补充前三大风险和对应预案。", "并附Top3风险及应对。"),
        ("checklist", "再给一个可以直接执行的每日清单版本。", "并附每日执行清单。"),
        ("constraints", "保持不用表格，表达更清晰，便于直接复制使用。", "并保持纯文本可直接使用。"),
        ("review", "增加每周复盘步骤和调整规则。", "并附每周复盘与调整机制。"),
        ("emergency", "加入突发情况分支：临时取消、延迟或超预算。", "并附突发分支决策流。"),
        ("family", "输出一份给家人看的简版和一份执行版。", "并附家人简版与执行版。"),
        ("final", "最终版要求：简洁、可执行、检查点不遗漏。", "并附最终精简执行版。"),
    ]
    variants_pos_en: List[Tuple[str, str, str]] = [
        ("budget", "Reduce budget by 10% and keep core outcomes stable.", "Include a 10%-budget-cut variant."),
        ("timeline", "Compress timeline by one week and mark non-removable steps.", "Include a one-week-compressed plan."),
        ("roles", "Add explicit role ownership and handoff checkpoints.", "Include role ownership and handoff checklist."),
        ("risk", "Add top-3 risks and mitigations.", "Include top-3 risks with mitigations."),
        ("checklist", "Provide a day-by-day operational checklist.", "Include a day-by-day checklist."),
        ("constraints", "Keep plain text output and avoid table formatting.", "Keep plain text, no tables."),
        ("review", "Add weekly review loop and adjustment rules.", "Include weekly review and adjustment loop."),
        ("emergency", "Add emergency branch for cancellations, delays, or budget overruns.", "Include emergency branch decisions."),
        ("dual_view", "Provide both stakeholder summary and executor view.", "Include stakeholder and executor views."),
        ("final", "Final version must be concise, actionable, and checkpoint-complete.", "Include final concise execution version."),
    ]
    variants_neg_zh: List[Tuple[str, str, str]] = [
        ("casual1", "再推荐一首歌就好。", "随便推荐一首歌。"),
        ("casual2", "顺便聊聊今天心情。", "聊聊今天心情。"),
        ("casual3", "再给一个轻松话题。", "给一个轻松话题。"),
        ("casual4", "推荐一部电影，不用解释。", "推荐一部电影。"),
        ("casual5", "给一个周末放松建议。", "给一个周末放松建议。"),
        ("casual6", "再说一个有趣冷知识。", "给一个冷知识。"),
        ("casual7", "一句话回答即可。", "一句话回答。"),
        ("casual8", "换个轻松点的话题。", "换个轻松话题。"),
        ("casual9", "今天先聊到这。", "先聊到这。"),
        ("casual10", "最后推荐一个播客。", "推荐一个播客。"),
    ]
    variants_neg_en: List[Tuple[str, str, str]] = [
        ("casual1", "Recommend one more song.", "Recommend one song."),
        ("casual2", "Share one fun fact.", "Share one fun fact."),
        ("casual3", "Give one light topic.", "Give one light topic."),
        ("casual4", "Suggest a movie in one line.", "Suggest one movie."),
        ("casual5", "Give one weekend relaxation tip.", "Give one relaxation tip."),
        ("casual6", "Keep it short and casual.", "Short casual reply only."),
        ("casual7", "No planning needed, just chat.", "No planning needed."),
        ("casual8", "Switch to a random topic.", "Random light topic."),
        ("casual9", "That is all for now.", "That is all."),
        ("casual10", "Recommend one podcast.", "Recommend one podcast."),
    ]

    families: List[Dict[str, Any]] = [
        {
            "template_id": "zh_family_travel_agent",
            "topic": "中文生活场景：家庭旅行规划 Agent",
            "objective": "围绕家庭旅行进行长期多轮协同，处理预算、成员差异、行程变化和应急预案。",
            "turns_seed": [
                "帮我规划一次6天家庭旅行，2个大人+1老人+1小孩。",
                "预算控制在1.5万以内，优先高铁，不坐红眼航班。",
                "老人膝盖不好，日均步行强度要低，安排午休。",
                "如遇天气变化，给室内备选和改签策略。",
                "最后输出执行版和家庭群简版。",
            ],
            "reuse_query": "给我一个家庭旅行长期协同方案，含预算、成员约束和天气预案。",
            "reuse_queries": ["生成家庭旅行执行清单。", "生成家庭旅行简版说明。"],
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_home_renovation_agent",
            "topic": "中文生活场景：装修项目管理 Agent",
            "objective": "在装修全流程中进行阶段化推进、验收和变更管理，形成可复用协作流程。",
            "turns_seed": [
                "帮我做一个两居室装修70天推进计划。",
                "先拆改和水电，隐蔽工程要重点把控。",
                "预算18万上限，主材环保且耐用。",
                "如果材料延期一周，工期怎么调度更稳？",
                "给施工队执行版和业主验收版。",
            ],
            "reuse_query": "生成装修项目推进方案，含预算控制、延期应对和验收节点。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_parent_school_coordination",
            "topic": "中文生活场景：家校协同学习管理 Agent",
            "objective": "围绕孩子学习目标进行家校协同、节奏调整与反馈闭环管理。",
            "turns_seed": [
                "给我做一个4周家校协同学习计划。",
                "周中每天1.5小时，周末3小时。",
                "数学薄弱、语文阅读慢、英语口语需保持。",
                "每周要和班主任同步一次，给沟通模板。",
                "状态不好时要有降载但不断档方案。",
            ],
            "reuse_query": "做一个家校协同学习方案，含沟通模板和降载策略。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_chronic_care_followup",
            "topic": "中文生活场景：慢病随访管理 Agent",
            "objective": "长期健康管理中沉淀提醒频率、异常升级、医生沟通摘要等可复用能力。",
            "turns_seed": [
                "帮我做父亲高血压随访计划。",
                "每天早晚记录血压，异常时要提醒复诊。",
                "提醒频率不能太打扰，尽量简洁。",
                "连续3天偏高就生成医生沟通摘要。",
                "每周给家属一个风险周报。",
            ],
            "reuse_query": "生成慢病随访流程，含提醒策略和异常升级规则。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_relocation_agent",
            "topic": "中文生活场景：搬家与迁居项目 Agent",
            "objective": "多阶段迁居任务中协调预算、时间、外部服务和家庭分工。",
            "turns_seed": [
                "帮我做一个6周跨城搬家计划。",
                "包括找房、搬家公司、水电网迁移、地址变更。",
                "预算上限5万，优先稳定可靠。",
                "搬家公司临时取消时要有12小时替代流程。",
                "给我、家人、父母三套分工清单。",
            ],
            "reuse_query": "生成跨城搬家执行方案，含分工清单和应急替代流程。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_wedding_planning_agent",
            "topic": "中文生活场景：婚礼筹备 Agent",
            "objective": "围绕婚礼筹备的里程碑管理、供应商协同与风险预案进行多轮优化。",
            "turns_seed": [
                "做一个4个月婚礼筹备计划，120人规模。",
                "拆分场地、餐饮、摄影、请柬等节点。",
                "预算30万以内，跟踪付款节点。",
                "下雨和供应商爽约要有预案。",
                "输出周计划和婚礼前72小时Runbook。",
            ],
            "reuse_query": "生成婚礼筹备执行流程，含里程碑、预算和风险预案。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_job_search_pipeline",
            "topic": "中文生活场景：求职流程管理 Agent",
            "objective": "在长期求职过程中管理申请节奏、反馈诊断、模拟面试与复盘。",
            "turns_seed": [
                "做一个10周产品经理求职计划。",
                "包括简历优化、投递、内推、模拟面试。",
                "每周投入不超过12小时，避免过载。",
                "回复率低于8%时触发诊断流程。",
                "给每周复盘模板和下周行动项。",
            ],
            "reuse_query": "生成可持续求职流程，含回复率诊断和周复盘机制。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_insurance_claim_agent",
            "topic": "中文生活场景：理赔流程协作 Agent",
            "objective": "理赔场景中沉淀证据整理、沟通节奏、拒赔申诉等可复用步骤。",
            "turns_seed": [
                "帮我处理一次家庭财产险理赔。",
                "按紧急程度列出证据收集顺序。",
                "和保险公司每3个工作日同步一次进度。",
                "如果部分拒赔，给申诉路径和补证清单。",
                "给家人看得懂的状态追踪表。",
            ],
            "reuse_query": "生成理赔协作流程，含证据顺序、沟通节奏和申诉路径。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_budget_recovery_agent",
            "topic": "中文生活场景：家庭预算恢复 Agent",
            "objective": "在家庭收支失衡后，通过多轮约束迭代恢复预算纪律并可持续执行。",
            "turns_seed": [
                "帮我做一个家庭预算恢复计划。",
                "先分固定支出、可协商支出、弹性支出。",
                "按周设置消费上限，保留应急例外规则。",
                "连续两周超支要自动触发纠偏动作。",
                "给双人家庭月度复盘流程。",
            ],
            "reuse_query": "生成家庭预算恢复流程，含超支纠偏与月度复盘。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_exam_prep_agent",
            "topic": "中文生活场景：考试备考 Agent",
            "objective": "长期备考中根据测试结果动态调参，沉淀学习节奏和应对策略。",
            "turns_seed": [
                "做一个14周职业考试备考计划。",
                "工作日每天90分钟，周末最多4小时。",
                "每两周根据模考分数调整重点。",
                "连续停滞时切到错题类型专项。",
                "最后给考前一周低压力执行清单。",
            ],
            "reuse_query": "生成可自适应的备考流程，含模考反馈调参和错题专项。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_pet_care_agent",
            "topic": "中文生活场景：宠物照护协同 Agent",
            "objective": "围绕宠物长期照护的喂养、运动、就医、代养交接进行流程化管理。",
            "turns_seed": [
                "帮我做一份狗狗每周照护计划。",
                "包含喂食、遛狗、洗护、驱虫和体重记录。",
                "下月要出差10天，加入代养交接流程。",
                "出现食欲下降要有就医升级规则。",
                "给我日常版和代养版两套清单。",
            ],
            "reuse_query": "生成宠物照护流程，含代养交接和异常升级规则。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_small_business_ops_agent",
            "topic": "中文生活场景：小店经营运营 Agent",
            "objective": "对小店日常经营中的排班、备货、活动、异常应对进行持续优化。",
            "turns_seed": [
                "帮我做一家咖啡小店的每周运营计划。",
                "包括排班、备货、促销、损耗控制。",
                "工作日和周末客流差异大，要分开策略。",
                "突发缺人时要有应急排班方案。",
                "最后给店长看板和店员执行清单。",
            ],
            "reuse_query": "生成小店运营流程，含排班、备货、应急和复盘。",
            "expect_extract": True,
            "complexity": "complex_agent_zh",
        },
        {
            "template_id": "zh_topic_switch_report_to_wechat",
            "topic": "中文主题切换：正式报告到公众号改写",
            "objective": "同一会话中切换任务目标与产物标准，检验新增技能与合并判定的边界。",
            "turns_seed": [
                "先写一份正式报告草案，主题是社区养老服务优化。",
                "要求正式、克制、可执行，不用表格。",
                "加责任分工和量化指标。",
                "现在切换任务：改写成公众号文章，面向普通家庭。",
                "语言更易懂，但不能编造事实。",
            ],
            "reuse_query": "写一篇面向普通读者的公众号文章，结构清晰、无表格。",
            "reuse_queries": ["写正式报告，强调责任分工和量化指标。"],
            "expect_extract": True,
            "complexity": "complex_switch_zh",
        },
        {
            "template_id": "en_family_travel_agent",
            "topic": "life agent: family travel orchestration",
            "objective": "Handle long-horizon travel planning with constraints, role coordination, and contingencies.",
            "turns_seed": [
                "Plan a 7-day family trip with one senior and one child.",
                "Keep budget below 4,000 USD and avoid overnight transfers.",
                "Limit walking load and include daily rest slots.",
                "Add weather fallback and transport delay contingency.",
                "Provide both detailed and compact execution versions.",
            ],
            "reuse_query": "Create a family travel workflow with budget guardrails and contingency branches.",
            "expect_extract": True,
            "complexity": "complex_agent",
        },
        {
            "template_id": "en_startup_ops_agent",
            "topic": "agent operations: startup weekly cadence",
            "objective": "Coordinate startup operations across hiring, runway, support load, and release rhythm.",
            "turns_seed": [
                "Set up a 12-week operating cadence for a small startup.",
                "Track hiring pipeline, runway, support load, and release milestones.",
                "Define owner checkpoints for weekly reviews.",
                "If runway drops below 5 months, trigger a cost-control branch.",
                "Output leadership summary and execution checklist.",
            ],
            "reuse_query": "Build a startup operations cadence with runway-triggered branch actions.",
            "expect_extract": True,
            "complexity": "complex_agent",
        },
        {
            "template_id": "zh_casual_small_talk",
            "topic": "中文负样例：闲聊",
            "objective": "多轮闲聊，不应形成稳定可复用技能。",
            "turns_seed": [
                "今天有点累，想聊点轻松的。",
                "推荐一部电影。",
                "再推荐一首歌。",
                "谢谢，差不多了。",
            ],
            "reuse_query": "推荐一部轻松电影。",
            "expect_extract": False,
            "complexity": "complex_negative_zh",
        },
        {
            "template_id": "one_off_fact_question",
            "topic": "one-off factual QA",
            "objective": "Single factual question, no durable user workflow preference.",
            "turns_seed": ["What is the difference between TCP and UDP?"],
            "reuse_query": "Explain TCP vs UDP briefly.",
            "expect_extract": False,
            "complexity": "basic_negative",
        },
        {
            "template_id": "single_translation",
            "topic": "single translation",
            "objective": "One-time translation request without persistent capability signal.",
            "turns_seed": ["Translate this sentence to English: 该系统支持在线增量更新。"],
            "reuse_query": "Translate: 模型会持续学习并更新技能。",
            "expect_extract": False,
            "complexity": "basic_negative",
        },
    ]

    out: List[EvalTemplate] = []
    for fam in families:
        template_id = str(fam.get("template_id") or "").strip()
        topic = str(fam.get("topic") or "").strip()
        objective = str(fam.get("objective") or "").strip()
        turns_seed = [str(x).strip() for x in list(fam.get("turns_seed") or []) if str(x).strip()]
        reuse_query = str(fam.get("reuse_query") or "").strip()
        reuse_queries = [str(x).strip() for x in list(fam.get("reuse_queries") or []) if str(x).strip()]
        expect_extract = bool(fam.get("expect_extract"))
        complexity = str(fam.get("complexity") or "basic")
        has_cjk = _has_cjk(topic) or _has_cjk(objective) or any(_has_cjk(x) for x in turns_seed)

        if expect_extract:
            variants = variants_pos_zh if has_cjk else variants_pos_en
        else:
            variants = variants_neg_zh if has_cjk else variants_neg_en

        for idx, (vname, vturn, vreuse) in enumerate(variants, start=1):
            turns = list(turns_seed)
            if vturn:
                turns.append(str(vturn).strip())

            rq = str(reuse_query)
            if rq and vreuse:
                rq = f"{rq}；{vreuse}" if has_cjk else f"{rq} {vreuse}"
            elif not rq:
                rq = str(vreuse or "").strip()

            rqs = list(reuse_queries)
            if rq and rq not in rqs:
                rqs.append(rq)

            out.append(
                EvalTemplate(
                    template_id=f"{template_id}__s{idx:02d}_{vname}",
                    topic=topic,
                    objective=objective,
                    turns_seed=turns,
                    reuse_query=rq,
                    expect_extract=expect_extract,
                    reuse_queries=rqs,
                    complexity=complexity,
                )
            )
    return out


def _expand_templates_for_min_coverage(
    templates: List[EvalTemplate],
    *,
    min_count: int,
) -> List[EvalTemplate]:
    """
    Expands base templates with deterministic variants until reaching min_count.
    Variants keep the same objective family but add extra constraints to improve
    robustness coverage.
    """

    out = list(templates or [])
    base = list(templates or [])
    if not base:
        return out
    target = max(len(base), int(min_count))
    if len(out) >= target:
        return out

    hints_en: List[Tuple[str, str, str]] = [
        (
            "no_markdown",
            "Do not use Markdown formatting; keep output directly usable in plain text editors.",
            "No markdown formatting; plain text only.",
        ),
        (
            "risk_checks",
            "Add explicit risk checks and acceptance criteria before final output.",
            "Include explicit risk checks and acceptance criteria.",
        ),
        (
            "concise_mode",
            "Keep the final output concise while preserving key constraints.",
            "Produce a concise version while preserving constraints.",
        ),
        (
            "counterexample",
            "Add one counterexample or failure mode and how to handle it.",
            "Include one failure mode and mitigation.",
        ),
    ]
    hints_zh: List[Tuple[str, str, str]] = [
        (
            "no_markdown",
            "不要使用 Markdown 排版，输出要能直接用于纯文本或 Word。",
            "不要 Markdown，输出纯文本/Word 可直接使用。",
        ),
        (
            "risk_checks",
            "补充风险检查项和验收标准，再给最终版本。",
            "补充风险检查项和验收标准。",
        ),
        (
            "concise_mode",
            "在不丢失约束的前提下给一个更精简版本。",
            "给出精简版但保留关键约束。",
        ),
        (
            "counterexample",
            "增加一个失败案例以及对应的处理方式。",
            "增加失败案例与应对策略。",
        ),
    ]

    idx = 0
    while len(out) < target:
        src = base[idx % len(base)]
        is_zh = _has_cjk(src.topic) or _has_cjk(src.objective) or any(_has_cjk(t) for t in (src.turns_seed or []))
        hints = hints_zh if is_zh else hints_en
        h_name, h_turn, h_reuse = hints[(idx // len(base)) % len(hints)]

        turns = list(src.turns_seed or [])
        if not turns:
            turns = [h_turn]
        else:
            turns = turns + [h_turn]

        reuse_q = str(src.reuse_query or "").strip()
        if reuse_q:
            if is_zh:
                reuse_q2 = f"{reuse_q}；{h_reuse}"
            else:
                reuse_q2 = f"{reuse_q} Also {h_reuse}"
        else:
            reuse_q2 = h_reuse

        rqs = list(src.reuse_queries or [])
        if reuse_q2 and reuse_q2 not in rqs:
            rqs.append(reuse_q2)

        variant_no = (idx // len(base)) + 1
        new_id = f"{src.template_id}__v{variant_no}_{h_name}"

        out.append(
            EvalTemplate(
                template_id=new_id,
                topic=str(src.topic),
                objective=str(src.objective),
                turns_seed=turns,
                reuse_query=reuse_q2,
                expect_extract=bool(src.expect_extract),
                reuse_queries=rqs,
                complexity=f"{src.complexity}_variant",
            )
        )
        idx += 1
    return out


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
        "- Preserve objective, constraints, and role context from seed turns.\n"
        "- Favor real human-agent collaboration patterns: planning, revisions, trade-offs, checkpoints.\n"
        "- Keep turns natural and concise; avoid generic filler.\n"
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
    order = list(range(len(templates)))
    rng.shuffle(order)
    out: List[EvalScenario] = []
    for i in range(max(1, int(runs))):
        t = templates[order[i % len(order)]]
        scenario_id = f"case_{i + 1:03d}_{t.template_id}"
        turns_seed = list(t.turns_seed)
        # Keep slight variation while preserving semantics.
        if len(turns_seed) >= 2 and rng.random() < 0.35:
            last = str(turns_seed[-1] or "")
            has_cjk = any(("\u4e00" <= ch <= "\u9fff") for ch in last)
            suffix = " 另外请保持简洁。" if has_cjk else " Also keep it concise."
            turns_seed[-1] = f"{last}{suffix}"
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


def _build_judge_client(
    *,
    judge_enabled: bool,
    judge_base_url: str,
    judge_api_key: str,
    judge_model: str,
    timeout_s: float,
) -> Optional[OpenAICompatLLMClient]:
    if not bool(judge_enabled):
        return None
    if not str(judge_api_key or "").strip():
        return None
    try:
        return OpenAICompatLLMClient(
            base_url=str(judge_base_url),
            api_key=str(judge_api_key),
            model=str(judge_model),
            timeout_s=float(timeout_s),
        )
    except Exception:
        return None


def _judge_overall_with_llm(
    *,
    judge_llm: OpenAICompatLLMClient,
    eval_result: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    summary = eval_result.get("summary") if isinstance(eval_result, dict) else {}
    cases = eval_result.get("cases") if isinstance(eval_result, dict) else []
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(cases, list):
        cases = []

    failed_examples: List[Dict[str, Any]] = []
    for c in cases:
        if not isinstance(c, dict):
            continue
        if bool(c.get("ok")):
            continue
        sc = c.get("scenario") if isinstance(c.get("scenario"), dict) else {}
        failed_examples.append(
            {
                "scenario_id": str(sc.get("id") or ""),
                "template_id": str(sc.get("template_id") or ""),
                "topic": str(sc.get("topic") or ""),
                "complexity": str(sc.get("complexity") or ""),
                "error": str(c.get("error") or ""),
            }
        )
        if len(failed_examples) >= 8:
            break

    system = (
        "You are an evaluation judge for AutoSkill benchmark reports.\n"
        "Return ONLY strict JSON with this schema:\n"
        "{"
        "\"overall_score\": 1-5,"
        "\"status\": \"good\"|\"warning\"|\"critical\","
        "\"strengths\": [\"...\"],"
        "\"risks\": [\"...\"],"
        "\"recommendations\": [\"...\"]"
        "}\n"
        "Judge the whole benchmark quality and extraction reliability."
    )
    user_payload = {
        "summary": summary,
        "failed_examples": failed_examples,
    }
    user = f"BENCHMARK_RESULT:\n{json.dumps(user_payload, ensure_ascii=False)}"
    out = judge_llm.chat_text(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.0,
        max_tokens=700,
    )
    parsed = _json_from_text(out)
    if not isinstance(parsed, dict):
        return None
    score_raw = parsed.get("overall_score")
    try:
        score = int(score_raw)
    except Exception:
        score = 0
    status = str(parsed.get("status") or "").strip().lower()
    if status not in {"good", "warning", "critical"}:
        status = "warning"

    def _to_list(v: Any, *, limit: int = 8) -> List[str]:
        if not isinstance(v, list):
            return []
        out2: List[str] = []
        for x in v:
            s = str(x or "").strip()
            if s:
                out2.append(s)
            if len(out2) >= int(limit):
                break
        return out2

    return {
        "overall_score": max(1, min(5, score)) if score else None,
        "status": status,
        "strengths": _to_list(parsed.get("strengths"), limit=8),
        "risks": _to_list(parsed.get("risks"), limit=8),
        "recommendations": _to_list(parsed.get("recommendations"), limit=8),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Health-check and evaluate AutoSkill proxy")
    parser.add_argument("--mode", default="health", choices=["health", "eval", "all"])
    parser.add_argument("--base-url", default="http://127.0.0.1:9000")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--user-id", default="proxy_test_user")
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout-s", type=float, default=25.0)
    parser.add_argument("--skip-embeddings", action="store_true")

    parser.add_argument("--eval-runs", type=int, default=32)
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
    parser.add_argument(
        "--judge-base-url",
        default=os.getenv("EVAL_JUDGE_BASE_URL", os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode")),
    )
    parser.add_argument(
        "--judge-api-key",
        default=os.getenv("EVAL_JUDGE_API_KEY", os.getenv("DASHSCOPE_API_KEY", "")),
    )
    parser.add_argument("--judge-model", default=os.getenv("EVAL_JUDGE_MODEL", "qwen-plus"))
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
        judge_llm = _build_judge_client(
            judge_enabled=bool(args.judge_enable),
            judge_base_url=str(args.judge_base_url),
            judge_api_key=str(args.judge_api_key),
            judge_model=str(args.judge_model),
            timeout_s=float(args.timeout_s),
        )
        if judge_llm is None and bool(args.judge_enable) and simulator is not None:
            # Backward-compatible fallback: reuse simulator client when explicit judge config is absent.
            judge_llm = simulator

        if simulator is None:
            print("[eval] simulator: disabled (using template turns)")
        else:
            print(f"[eval] simulator: enabled model={args.sim_model}")
        if judge_llm is not None:
            print(f"[eval] judge: enabled model={args.judge_model}")
        elif bool(args.judge_enable):
            print("[eval] judge: enabled but client init failed (check judge api key/model/base url)")

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
        if judge_llm is not None:
            try:
                overall_judge = _judge_overall_with_llm(
                    judge_llm=judge_llm,
                    eval_result=eval_result,
                )
            except Exception as e:
                overall_judge = {"error": str(e)}
            eval_result["overall_judge"] = overall_judge

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
                    "overall_judge": (eval_result.get("overall_judge") if isinstance(eval_result, dict) else None),
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
