"""
AutoSkill automatic evolution evaluation script (LLM-vs-LLM).

Usage:
  python3 -m examples.auto_evalution \
    --mode eval \
    --eval-strategy evolution \
    --base-url http://127.0.0.1:9000 \
    --sim-provider qwen \
    --sim-api-key "$AUTOSKILL_PROXY_API_KEY" \
    --sim-model qwen-plus \
    --judge-provider qwen \
    --judge-model qwen-plus \
    --judge-api-key "$AUTOSKILL_PROXY_API_KEY"
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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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
    Lightweight OpenAI-compatible chat caller for simulator models.
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


def _proxy_chat_payload(user_id: str, *, stream: bool, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "model": str(model),
        "stream": bool(stream),
        # Keep evaluation deterministic to reduce score noise across before/after.
        "temperature": 0.0,
        "max_tokens": 2048,
        "user": str(user_id),
        "messages": list(messages),
    }


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


def _proxy_chat_once(
    *,
    client: HTTPClient,
    model: str,
    user_id: str,
    messages: List[Dict[str, str]],
    chat_stream: bool,
    turn_timeout_s: float,
) -> Tuple[str, Dict[str, Any]]:
    payload = _proxy_chat_payload(
        user_id=user_id,
        stream=bool(chat_stream),
        model=model,
        messages=list(messages),
    )
    prev_timeout = client.timeout_s
    client.timeout_s = float(turn_timeout_s)
    try:
        if bool(chat_stream):
            stream_obj = client.request_stream_chat(path="/v1/chat/completions", payload=payload)
            err = str(stream_obj.get("error") or "").strip()
            if err:
                raise RuntimeError(f"stream error: {err}")
            text = str(stream_obj.get("content") or "").strip() or "(empty response)"
            raw = stream_obj.get("autoskill")
            diag = dict(raw) if isinstance(raw, dict) else {}
            return text, diag
        obj = client.request_json(method="POST", path="/v1/chat/completions", payload=payload)
        text = _extract_chat_content(obj) or "(empty response)"
        raw = obj.get("autoskill")
        diag = dict(raw) if isinstance(raw, dict) else {}
        return str(text).strip(), diag
    finally:
        client.timeout_s = prev_timeout


def _judge_task_success(
    *,
    judge_llm: OpenAICompatLLMClient,
    scenario: EvalScenario,
    query: str,
    answer: str,
    requirement_contract: Optional[Dict[str, Any]],
    stage: str,
    success_threshold: float,
) -> Dict[str, Any]:
    system = (
        "You are a strict task-success judge for AutoSkill evaluation.\n"
        "Score only the assistant answer quality against user requirements and constraints.\n"
        "Treat requirement_contract as the primary scoring basis.\n"
        "Infer explicit user requirements from the conversation turns and query before scoring.\n"
        "Use this priority order when resolving constraints:\n"
        "1) requirement_contract\n"
        "2) evaluation_query (direct ask)\n"
        "3) recent_focus_turns (latest user constraints)\n"
        "4) final_turns (full evolved context)\n"
        "5) seed_turns (early context)\n"
        "6) objective (high-level intent only, NOT a hard requirement list)\n"
        "When constraints evolve, prioritize newer constraints from recent turns.\n"
        "If old and new constraints conflict, follow newer constraints.\n"
        "Do NOT penalize missing details that were never requested.\n"
        "This is an independent test answer; do not assume hidden context beyond provided data.\n"
        "Output STRICT JSON only:\n"
        "{\"score\": 0-100, \"success\": true|false, \"reason\": \"...\", \"strengths\": [\"...\"], \"gaps\": [\"...\"], "
        "\"constraint_coverage\": {\"critical_met\": 0, \"critical_total\": 0, \"overall_ratio\": 0.0}, "
        "\"resolved_constraints\": {\"critical\": [\"...\"], \"important\": [\"...\"]}, "
        "\"violations\": [\"...\"]}\n"
        "Scoring rubric:\n"
        "- 90-100: fully satisfies objective and key constraints, clear and actionable.\n"
        "- 70-89: mostly satisfies objective, minor gaps.\n"
        "- 50-69: partially satisfies objective, notable misses.\n"
        "- 0-49: fails key objective/constraints.\n"
        "Critical constraints include explicit hard requirements such as format/platform/style/forbidden elements.\n"
        "Set success=true only when score >= threshold and all critical constraints are met.\n"
        f"Set success=true when score >= {float(success_threshold):.1f}.\n"
    )
    payload = {
        "stage": str(stage or ""),
        "topic": str(scenario.topic or ""),
        "objective": str(scenario.objective or ""),
        "objective_role": "high-level task intent only",
        "requirement_contract": dict(requirement_contract or {}),
        "requirement_contract_role": "primary scoring basis",
        "evaluation_query": str(query or ""),
        "evaluation_query_role": "independent re-test input",
        "assistant_answer": str(answer or ""),
        "seed_turns": list(scenario.turns_seed or []),
        "final_turns": list(scenario.turns_final or []),
        "recent_focus_turns": list((scenario.turns_final or scenario.turns_seed or [])[-6:]),
        "independent_test": True,
        "answer_generated_from_single_turn_query": True,
        "constraint_priority_order": [
            "requirement_contract",
            "evaluation_query",
            "recent_focus_turns",
            "final_turns",
            "seed_turns",
            "objective",
        ],
    }
    user = f"DATA:\n{json.dumps(payload, ensure_ascii=False)}"
    out = judge_llm.chat_text(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.0,
        max_tokens=1200,
    )
    parsed = _json_from_text(out) or {}
    score_raw = parsed.get("score", 0)
    try:
        score = float(score_raw)
    except Exception:
        score = 0.0
    score = max(0.0, min(100.0, float(score)))
    success_raw = parsed.get("success")
    coverage_in = parsed.get("constraint_coverage")
    coverage = dict(coverage_in) if isinstance(coverage_in, dict) else {}
    critical_total = int(coverage.get("critical_total") or 0)
    critical_met = int(coverage.get("critical_met") or 0)
    all_critical_met = True if critical_total <= 0 else (critical_met >= critical_total)
    success = bool(success_raw) if isinstance(success_raw, bool) else (score >= float(success_threshold))
    if not all_critical_met:
        success = False
    reason = str(parsed.get("reason") or "").strip()
    strengths_in = parsed.get("strengths")
    gaps_in = parsed.get("gaps")
    resolved_in = parsed.get("resolved_constraints")
    violations_in = parsed.get("violations")
    strengths = [str(x).strip() for x in (strengths_in if isinstance(strengths_in, list) else []) if str(x).strip()]
    gaps = [str(x).strip() for x in (gaps_in if isinstance(gaps_in, list) else []) if str(x).strip()]
    resolved = dict(resolved_in) if isinstance(resolved_in, dict) else {}
    critical_constraints = [
        str(x).strip()
        for x in (resolved.get("critical") if isinstance(resolved.get("critical"), list) else [])
        if str(x).strip()
    ]
    important_constraints = [
        str(x).strip()
        for x in (resolved.get("important") if isinstance(resolved.get("important"), list) else [])
        if str(x).strip()
    ]
    violations = [str(x).strip() for x in (violations_in if isinstance(violations_in, list) else []) if str(x).strip()]
    return {
        "score": score,
        "success": bool(success),
        "reason": reason,
        "strengths": strengths,
        "gaps": gaps,
        "resolved_constraints": {"critical": critical_constraints, "important": important_constraints},
        "violations": violations,
        "constraint_coverage": {
            "critical_met": int(critical_met),
            "critical_total": int(critical_total),
            "overall_ratio": float(coverage.get("overall_ratio") or 0.0),
        },
        "raw": str(out or ""),
    }


def _evaluate_stage_with_queries(
    *,
    client: HTTPClient,
    model: str,
    user_id: str,
    scenario: EvalScenario,
    queries: List[str],
    stage: str,
    chat_stream: bool,
    turn_timeout_s: float,
    judge_llm: OpenAICompatLLMClient,
    requirement_contract: Optional[Dict[str, Any]],
    success_threshold: float,
) -> Dict[str, Any]:
    used_queries = [str(q).strip() for q in list(queries or []) if str(q).strip()]
    if not used_queries:
        used_queries = [str(scenario.objective or "").strip() or "Provide your best final answer for this task."]

    items: List[Dict[str, Any]] = []
    success_n = 0
    score_sum = 0.0
    for q in used_queries:
        messages = [
            {
                "role": "system",
                "content": (
                    "Independent benchmark mode: answer only from this request. "
                    "Do not rely on prior chat turns not included in this request."
                ),
            },
            {"role": "user", "content": q},
        ]
        ans, autoskill_diag = _proxy_chat_once(
            client=client,
            model=model,
            user_id=user_id,
            messages=messages,
            chat_stream=bool(chat_stream),
            turn_timeout_s=float(turn_timeout_s),
        )
        j = _judge_task_success(
            judge_llm=judge_llm,
            scenario=scenario,
            query=q,
            answer=ans,
            requirement_contract=dict(requirement_contract or {}),
            stage=stage,
            success_threshold=float(success_threshold),
        )
        score = float(j.get("score") or 0.0)
        score_sum += score
        if bool(j.get("success")):
            success_n += 1
        items.append(
            {
                "query": q,
                "answer": ans,
                "autoskill": autoskill_diag,
                "judge": j,
            }
        )

    n = max(1, len(items))
    avg_score = float(score_sum / n)
    success_rate = float(success_n / n)
    # Majority success on multi-query evaluation to reduce single-query noise.
    stage_success = bool(success_rate >= 0.5)
    return {
        "items": items,
        "judge": {
            "score": avg_score,
            "success": stage_success,
            "reason": f"Aggregated over {n} eval queries.",
            "strengths": [],
            "gaps": [],
            "success_rate": success_rate,
            "query_count": n,
        },
    }


def _build_requirement_contract(
    *,
    judge_llm: OpenAICompatLLMClient,
    scenario: EvalScenario,
    eval_queries_seed: List[str],
) -> Dict[str, Any]:
    """
    Build a compact requirement contract from user turns.
    This becomes the primary scoring basis to reduce objective-driven bias.
    """
    system = (
        "You are a requirement extractor for AutoSkill evaluation.\n"
        "Summarize user requirements from the conversation, prioritizing recent turns.\n"
        "Output STRICT JSON only:\n"
        "{\"task\":\"...\", \"hard_constraints\":[\"...\"], \"soft_preferences\":[\"...\"], "
        "\"acceptance_checks\":[\"...\"], \"eval_queries\":[\"...\"]}\n"
        "Rules:\n"
        "- Base primarily on recent user turns; keep older turns only if still valid.\n"
        "- Treat objective as high-level background, not hard constraints.\n"
        "- Keep constraints concise and testable.\n"
        "- Generate 1-2 independent re-test queries that verify requirement adherence.\n"
    )
    payload = {
        "topic": str(scenario.topic or ""),
        "objective": str(scenario.objective or ""),
        "seed_turns": list(scenario.turns_seed or []),
        "final_turns": list(scenario.turns_final or []),
        "recent_focus_turns": list((scenario.turns_final or scenario.turns_seed or [])[-6:]),
        "reuse_queries_seed": [str(x).strip() for x in list(eval_queries_seed or []) if str(x).strip()],
    }
    user = f"DATA:\n{json.dumps(payload, ensure_ascii=False)}"
    try:
        out = judge_llm.chat_text(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=900,
        )
        parsed = _json_from_text(out) or {}
    except Exception:
        parsed = {}

    task = str(parsed.get("task") or "").strip()
    if not task:
        task = str(scenario.topic or "").strip() or "Complete the user task faithfully."
    hard = [str(x).strip() for x in list(parsed.get("hard_constraints") or []) if str(x).strip()]
    soft = [str(x).strip() for x in list(parsed.get("soft_preferences") or []) if str(x).strip()]
    checks = [str(x).strip() for x in list(parsed.get("acceptance_checks") or []) if str(x).strip()]
    eval_queries = [str(x).strip() for x in list(parsed.get("eval_queries") or []) if str(x).strip()]
    if not eval_queries:
        eval_queries = [str(x).strip() for x in list(eval_queries_seed or []) if str(x).strip()]
    if not eval_queries:
        # Prefer the latest user ask for independent testing when no explicit query is available.
        recent_turns = [str(x).strip() for x in list(scenario.turns_final or scenario.turns_seed or []) if str(x).strip()]
        if recent_turns:
            eval_queries = [recent_turns[-1]]
    return {
        "task": task,
        "hard_constraints": hard,
        "soft_preferences": soft,
        "acceptance_checks": checks,
        "eval_queries": eval_queries[:2],
    }


def _run_eval_case_evolution(
    *,
    client: HTTPClient,
    model: str,
    scenario: EvalScenario,
    user_prefix: str,
    run_nonce: str,
    chat_stream: bool,
    turn_timeout_s: float,
    extraction_timeout_s: float,
    poll_interval_s: float,
    judge_llm: OpenAICompatLLMClient,
    judge_success_threshold: float,
    max_train_turns: int,
    verbose: bool,
) -> Dict[str, Any]:
    case_start = time.time()
    base_user = f"{user_prefix}_{scenario.scenario_id}_{run_nonce}_base"
    evo_user = f"{user_prefix}_{scenario.scenario_id}_{run_nonce}_evo"
    eval_query = str(scenario.reuse_query or "").strip()
    eval_queries_seed: List[str] = []
    for q in list(scenario.reuse_queries or []):
        s = str(q).strip()
        if s and s not in eval_queries_seed:
            eval_queries_seed.append(s)
    if eval_query and eval_query not in eval_queries_seed:
        eval_queries_seed.insert(0, eval_query)
    requirement_contract = _build_requirement_contract(
        judge_llm=judge_llm,
        scenario=scenario,
        eval_queries_seed=eval_queries_seed,
    )
    eval_queries = [str(x).strip() for x in list(requirement_contract.get("eval_queries") or []) if str(x).strip()]
    if not eval_queries:
        eval_queries = list(eval_queries_seed)
    if not eval_queries:
        eval_queries = [str(scenario.topic or "").strip() or "Provide your best final answer for this task."]
    eval_query = str(eval_queries[0] or "").strip()
    # Keep evaluation runtime stable while reducing single-query variance.
    eval_queries = eval_queries[:2]

    print(
        f"[evo][case] start id={scenario.scenario_id} topic={scenario.topic} "
        f"base_user={base_user} evo_user={evo_user}"
    )

    # A) Baseline (no prior user skills) -> judge score.
    baseline_eval = _evaluate_stage_with_queries(
        client=client,
        model=model,
        user_id=base_user,
        scenario=scenario,
        queries=eval_queries,
        stage="before_evolution",
        chat_stream=bool(chat_stream),
        turn_timeout_s=float(turn_timeout_s),
        judge_llm=judge_llm,
        requirement_contract=requirement_contract,
        success_threshold=float(judge_success_threshold),
    )
    baseline_items = list(baseline_eval.get("items") or [])
    baseline_judge = dict(baseline_eval.get("judge") or {})
    baseline_answer = str((baseline_items[0].get("answer") if baseline_items else "") or "")
    baseline_autoskill = dict((baseline_items[0].get("autoskill") if baseline_items else {}) or {})

    # B) Evolution: run full conversation to trigger extraction/maintenance.
    train_messages: List[Dict[str, str]] = []
    train_turns_raw = list(scenario.turns_final or scenario.turns_seed or [])
    train_turns = [str(x).strip() for x in train_turns_raw if str(x).strip()]
    lim = max(1, int(max_train_turns or 1))
    if len(train_turns) > lim:
        train_turns = train_turns[:lim]
    train_records: List[Dict[str, Any]] = []
    job_ids: List[str] = []
    for idx, user_turn in enumerate(train_turns, start=1):
        train_messages.append({"role": "user", "content": user_turn})
        assistant_text, autoskill = _proxy_chat_once(
            client=client,
            model=model,
            user_id=evo_user,
            messages=train_messages,
            chat_stream=bool(chat_stream),
            turn_timeout_s=float(turn_timeout_s),
        )
        train_messages.append({"role": "assistant", "content": assistant_text})

        extraction_diag = autoskill.get("extraction")
        job_id = ""
        status = "unknown"
        if isinstance(extraction_diag, dict):
            job_id = str(extraction_diag.get("job_id") or "").strip()
            status = str(extraction_diag.get("status") or "unknown").strip().lower()
        if job_id and job_id not in job_ids:
            job_ids.append(job_id)
        retrieval_diag = autoskill.get("retrieval")
        retrieval_obj = dict(retrieval_diag) if isinstance(retrieval_diag, dict) else {}
        train_records.append(
            {
                "turn_index": int(idx),
                "user": user_turn,
                "assistant": assistant_text,
                "autoskill": {
                    "retrieval": retrieval_obj,
                    "extraction": {"job_id": (job_id or None), "status": status},
                },
            }
        )
        if verbose:
            print(
                f"[evo][train] case={scenario.scenario_id} idx={idx} "
                f"extract_status={status} job_id={job_id or '-'}"
            )

    events_by_job: Dict[str, Dict[str, Any]] = {}
    for jid in job_ids:
        if verbose:
            print(f"[evo][extract] case={scenario.scenario_id} poll job_id={jid}")
        ev = _poll_extraction_event(
            client,
            job_id=jid,
            timeout_s=float(extraction_timeout_s),
            poll_interval_s=float(poll_interval_s),
        )
        events_by_job[jid] = ev

    completed = [e for e in events_by_job.values() if str(e.get("status") or "").strip().lower() == "completed"]
    upserted_total = 0
    evolved_skill_ids: List[str] = []
    for ev in completed:
        ups = ev.get("upserted")
        if isinstance(ups, list):
            upserted_total += len(ups)
            for u in ups:
                if isinstance(u, dict):
                    sid = str(u.get("id") or "").strip()
                    if sid and sid not in evolved_skill_ids:
                        evolved_skill_ids.append(sid)

    # C) Post-evolution evaluation on same scenario query set -> judge score.
    post_eval = _evaluate_stage_with_queries(
        client=client,
        model=model,
        user_id=evo_user,
        scenario=scenario,
        queries=eval_queries,
        stage="after_evolution",
        chat_stream=bool(chat_stream),
        turn_timeout_s=float(turn_timeout_s),
        judge_llm=judge_llm,
        requirement_contract=requirement_contract,
        success_threshold=float(judge_success_threshold),
    )
    post_items = list(post_eval.get("items") or [])
    post_judge = dict(post_eval.get("judge") or {})
    post_answer = str((post_items[0].get("answer") if post_items else "") or "")
    post_autoskill = dict((post_items[0].get("autoskill") if post_items else {}) or {})

    before_success = bool(baseline_judge.get("success"))
    after_success = bool(post_judge.get("success"))
    sr_delta = int(after_success) - int(before_success)
    score_before = float(baseline_judge.get("score") or 0.0)
    score_after = float(post_judge.get("score") or 0.0)
    score_delta = score_after - score_before
    elapsed_s = float(time.time() - case_start)
    print(
        f"[evo][case] done id={scenario.scenario_id} elapsed_s={elapsed_s:.2f} "
        f"before_success={int(before_success)} after_success={int(after_success)} "
        f"score_before={score_before:.1f} score_after={score_after:.1f} "
        f"upserted={upserted_total}"
    )

    return {
        "scenario": {
            "id": scenario.scenario_id,
            "template_id": scenario.template_id,
            "topic": scenario.topic,
            "objective": scenario.objective,
            "source": scenario.source,
            "complexity": scenario.complexity,
            "turns_seed": list(scenario.turns_seed),
            "turns_final": list(scenario.turns_final),
            "reuse_query": scenario.reuse_query,
            "reuse_queries": list(scenario.reuse_queries or []),
        },
        "users": {"baseline_user": base_user, "evolved_user": evo_user},
        "requirement_contract": dict(requirement_contract),
        "evaluation_query": eval_query,
        "evaluation_queries": list(eval_queries),
        "baseline": {
            "answer": baseline_answer,
            "autoskill": baseline_autoskill,
            "items": baseline_items,
            "judge": baseline_judge,
        },
        "evolution": {
            "train_turns": train_records,
            "job_ids": list(job_ids),
            "events_by_job": events_by_job,
            "upserted_total": int(upserted_total),
            "skill_ids": list(evolved_skill_ids),
        },
        "post_evolution": {
            "answer": post_answer,
            "autoskill": post_autoskill,
            "items": post_items,
            "judge": post_judge,
        },
        "success": {
            "before": bool(before_success),
            "after": bool(after_success),
            "delta": int(sr_delta),
        },
        "scores": {
            "before": float(score_before),
            "after": float(score_after),
            "delta": float(score_delta),
        },
        "elapsed_s": elapsed_s,
    }


def run_eval_evolution(
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
    simulator: OpenAICompatLLMClient,
    judge_llm: OpenAICompatLLMClient,
    judge_success_threshold: float,
    max_train_turns: int,
    verbose: bool,
) -> Dict[str, Any]:
    scenarios = _sample_scenarios(
        runs=eval_runs,
        seed=eval_seed,
        simulator=simulator,
        verbose=verbose,
    )
    sampled_scenarios: List[Dict[str, Any]] = []
    for sc in scenarios:
        sampled_scenarios.append(
            {
                "id": sc.scenario_id,
                "template_id": sc.template_id,
                "topic": sc.topic,
                "objective": sc.objective,
                "source": sc.source,
                "complexity": sc.complexity,
                "expect_extract": bool(sc.expect_extract),
                "turns_seed": list(sc.turns_seed or []),
                "turns_final": list(sc.turns_final or []),
                "reuse_query": str(sc.reuse_query or ""),
                "reuse_queries": list(sc.reuse_queries or []),
            }
        )
    run_nonce = f"r{int(time.time())}_{random.randint(1000, 9999)}"
    cases: List[Dict[str, Any]] = []
    start_ts = time.time()

    for i, sc in enumerate(scenarios, start=1):
        print(
            f"[evo] running {i}/{len(scenarios)} id={sc.scenario_id} "
            f"template={sc.template_id} source={sc.source} complexity={sc.complexity}"
        )
        try:
            case = _run_eval_case_evolution(
                client=client,
                model=model,
                scenario=sc,
                user_prefix=user_prefix,
                run_nonce=run_nonce,
                chat_stream=bool(eval_stream),
                turn_timeout_s=float(turn_timeout_s),
                extraction_timeout_s=float(extraction_timeout_s),
                poll_interval_s=float(poll_interval_s),
                judge_llm=judge_llm,
                judge_success_threshold=float(judge_success_threshold),
                max_train_turns=int(max_train_turns),
                verbose=bool(verbose),
            )
            case["ok"] = True
            case["error"] = ""
        except Exception as e:
            tb = traceback.format_exc(limit=6)
            print(f"[evo] FAIL id={sc.scenario_id}: {e}")
            if verbose:
                print(f"[evo] traceback id={sc.scenario_id}:\n{tb}")
            case = {
                "scenario": {
                    "id": sc.scenario_id,
                    "template_id": sc.template_id,
                    "topic": sc.topic,
                    "objective": sc.objective,
                    "source": sc.source,
                    "complexity": sc.complexity,
                },
                "ok": False,
                "error": str(e),
                "traceback": tb,
            }
        cases.append(case)

    elapsed_s = float(time.time() - start_ts)
    ok_cases = [c for c in cases if bool(c.get("ok"))]
    ok_n = len(ok_cases)

    success_before_n = 0
    success_after_n = 0
    extracted_case_n = 0
    score_before_sum = 0.0
    score_after_sum = 0.0
    score_delta_sum = 0.0
    for c in ok_cases:
        suc = c.get("success") if isinstance(c, dict) else {}
        if isinstance(suc, dict):
            if bool(suc.get("before")):
                success_before_n += 1
            if bool(suc.get("after")):
                success_after_n += 1
        evo = c.get("evolution") if isinstance(c, dict) else {}
        if isinstance(evo, dict):
            if int(evo.get("upserted_total") or 0) > 0:
                extracted_case_n += 1
        scs = c.get("scores") if isinstance(c, dict) else {}
        if isinstance(scs, dict):
            score_before_sum += float(scs.get("before") or 0.0)
            score_after_sum += float(scs.get("after") or 0.0)
            score_delta_sum += float(scs.get("delta") or 0.0)

    sr_before = (float(success_before_n) / max(1, ok_n))
    sr_after = (float(success_after_n) / max(1, ok_n))
    sr_uplift_abs = sr_after - sr_before
    sr_uplift_rel = (sr_uplift_abs / sr_before) if sr_before > 0 else None
    avg_score_before = (score_before_sum / max(1, ok_n))
    avg_score_after = (score_after_sum / max(1, ok_n))
    avg_score_delta = (score_delta_sum / max(1, ok_n))
    extraction_case_rate = (float(extracted_case_n) / max(1, ok_n))

    metric_guide = {
        "sr_before": "Task Success Rate before skill evolution. Formula: success_before / ok_cases.",
        "sr_after": "Task Success Rate after skill evolution. Formula: success_after / ok_cases.",
        "sr_uplift_abs": "Absolute SR uplift. Formula: sr_after - sr_before.",
        "sr_uplift_rel": "Relative SR uplift. Formula: (sr_after - sr_before) / sr_before.",
        "avg_score_before": "Average LLM-judge score before evolution (0-100).",
        "avg_score_after": "Average LLM-judge score after evolution (0-100).",
        "avg_score_delta": "Average score improvement after evolution.",
        "extraction_case_rate": "Fraction of ok cases where at least one skill was upserted.",
    }

    summary = {
        "strategy": "evolution",
        "total_cases": len(cases),
        "ok_cases": ok_n,
        "failed_cases": len(cases) - ok_n,
        "elapsed_s": elapsed_s,
        "judge_success_threshold": float(judge_success_threshold),
        "metrics": {
            "sr_before": sr_before,
            "sr_after": sr_after,
            "sr_uplift_abs": sr_uplift_abs,
            "sr_uplift_rel": sr_uplift_rel,
            "avg_score_before": avg_score_before,
            "avg_score_after": avg_score_after,
            "avg_score_delta": avg_score_delta,
            "extraction_case_rate": extraction_case_rate,
        },
        "counts": {
            "success_before": int(success_before_n),
            "success_after": int(success_after_n),
            "extracted_cases": int(extracted_case_n),
        },
        "automation": {
            "user_role": "LLM simulator generates and executes multi-turn user interactions.",
            "assistant_role": "Proxy target model responds and triggers skill evolution.",
            "judge_role": "LLM judge scores pre/post task outputs with strict JSON rubric.",
        },
        "metric_guide": metric_guide,
    }
    return {"summary": summary, "sampled_scenarios": sampled_scenarios, "cases": cases}


def _build_case_analysis_rows(eval_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    cases = eval_result.get("cases") if isinstance(eval_result, dict) else None
    if not isinstance(cases, list):
        return rows
    for c in cases:
        if not isinstance(c, dict):
            continue
        sc = c.get("scenario")
        baseline = c.get("baseline")
        post = c.get("post_evolution")
        evolution = c.get("evolution")
        success = c.get("success")
        scores = c.get("scores")

        sc_obj = dict(sc) if isinstance(sc, dict) else {}
        baseline_obj = dict(baseline) if isinstance(baseline, dict) else {}
        post_obj = dict(post) if isinstance(post, dict) else {}
        evo_obj = dict(evolution) if isinstance(evolution, dict) else {}
        success_obj = dict(success) if isinstance(success, dict) else {}
        score_obj = dict(scores) if isinstance(scores, dict) else {}

        bj = baseline_obj.get("judge")
        pj = post_obj.get("judge")
        bj_obj = dict(bj) if isinstance(bj, dict) else {}
        pj_obj = dict(pj) if isinstance(pj, dict) else {}

        rows.append(
            {
                "ok": bool(c.get("ok")),
                "error": str(c.get("error") or ""),
                "scenario_id": str(sc_obj.get("id") or ""),
                "template_id": str(sc_obj.get("template_id") or ""),
                "topic": str(sc_obj.get("topic") or ""),
                "objective": str(sc_obj.get("objective") or ""),
                "source": str(sc_obj.get("source") or ""),
                "complexity": str(sc_obj.get("complexity") or ""),
                "turns_seed": list(sc_obj.get("turns_seed") or []),
                "turns_final": list(sc_obj.get("turns_final") or []),
                "requirement_contract": dict(c.get("requirement_contract") or {}),
                "evaluation_query": str(c.get("evaluation_query") or ""),
                "evaluation_queries": list(c.get("evaluation_queries") or []),
                "baseline": {
                    "answer": str(baseline_obj.get("answer") or ""),
                    "score": float(bj_obj.get("score") or 0.0),
                    "success": bool(bj_obj.get("success")),
                    "reason": str(bj_obj.get("reason") or ""),
                    "strengths": list(bj_obj.get("strengths") or []),
                    "gaps": list(bj_obj.get("gaps") or []),
                    "resolved_constraints": dict(bj_obj.get("resolved_constraints") or {}),
                    "violations": list(bj_obj.get("violations") or []),
                    "constraint_coverage": dict(bj_obj.get("constraint_coverage") or {}),
                    "success_rate": float(bj_obj.get("success_rate") or 0.0),
                    "query_count": int(bj_obj.get("query_count") or 0),
                },
                "post_evolution": {
                    "answer": str(post_obj.get("answer") or ""),
                    "score": float(pj_obj.get("score") or 0.0),
                    "success": bool(pj_obj.get("success")),
                    "reason": str(pj_obj.get("reason") or ""),
                    "strengths": list(pj_obj.get("strengths") or []),
                    "gaps": list(pj_obj.get("gaps") or []),
                    "resolved_constraints": dict(pj_obj.get("resolved_constraints") or {}),
                    "violations": list(pj_obj.get("violations") or []),
                    "constraint_coverage": dict(pj_obj.get("constraint_coverage") or {}),
                    "success_rate": float(pj_obj.get("success_rate") or 0.0),
                    "query_count": int(pj_obj.get("query_count") or 0),
                },
                "evolution": {
                    "upserted_total": int(evo_obj.get("upserted_total") or 0),
                    "skill_ids": list(evo_obj.get("skill_ids") or []),
                    "job_ids": list(evo_obj.get("job_ids") or []),
                },
                "delta": {
                    "success_delta": int(success_obj.get("delta") or 0),
                    "score_delta": float(score_obj.get("delta") or 0.0),
                },
            }
        )
    return rows


def _persist_eval_outputs(
    *,
    report: Dict[str, Any],
    eval_result: Dict[str, Any],
    report_json_arg: str,
) -> Tuple[str, str]:
    ts = int(time.time())
    requested = str(report_json_arg or "").strip()
    if requested:
        report_path = Path(requested)
        if not report_path.is_absolute():
            report_path = Path.cwd() / report_path
    else:
        report_path = Path.cwd() / "examples" / "eval_reports" / f"auto_evalution_report_{ts}.json"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    analysis_path = report_path.with_name(f"{report_path.stem}_analysis.jsonl")

    report_out = dict(report)
    eval_out = dict(eval_result) if isinstance(eval_result, dict) else {}
    eval_out["case_analysis"] = _build_case_analysis_rows(eval_out)
    report_out["evaluation"] = eval_out

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_out, f, ensure_ascii=False, indent=2)

    with open(analysis_path, "w", encoding="utf-8") as f:
        for row in list(eval_out.get("case_analysis") or []):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return str(report_path), str(analysis_path)


def _build_simulator_client(
    *,
    sim_provider: str,
    sim_api_key: str,
    sim_model: str,
    default_base_url: str,
    default_api_key: str,
    default_model: str,
    timeout_s: float,
) -> Optional[OpenAICompatLLMClient]:
    base, api_key, _ = _resolve_llm_endpoint(
        provider=str(sim_provider or ""),
        explicit_base_url="",
        explicit_api_key=str(sim_api_key or ""),
        default_base_url=str(default_base_url or ""),
        default_api_key=str(default_api_key or ""),
    )
    model = str(sim_model or "").strip() or str(default_model or "").strip()
    if not model:
        return None
    if not base:
        return None
    try:
        return OpenAICompatLLMClient(
            base_url=base,
            api_key=api_key,
            model=model,
            timeout_s=float(timeout_s),
        )
    except Exception:
        return None


def _build_judge_client(
    *,
    judge_provider: str,
    judge_api_key: str,
    judge_model: str,
    default_base_url: str,
    default_api_key: str,
    default_model: str,
    timeout_s: float,
) -> Optional[OpenAICompatLLMClient]:
    base, api_key, _ = _resolve_llm_endpoint(
        provider=str(judge_provider or ""),
        explicit_base_url="",
        explicit_api_key=str(judge_api_key or ""),
        default_base_url=str(default_base_url or ""),
        default_api_key=str(default_api_key or ""),
    )
    model = str(judge_model or "").strip() or str(default_model or "").strip()
    if not model:
        return None
    if not base:
        return None
    try:
        return OpenAICompatLLMClient(
            base_url=base,
            api_key=api_key,
            model=model,
            timeout_s=float(timeout_s),
        )
    except Exception:
        return None


def _normalize_provider(provider: str) -> str:
    p = str(provider or "").strip().lower()
    aliases = {
        "qwen": "dashscope",
        "intern": "internlm",
        "intern-s1": "internlm",
        "intern-s1-pro": "internlm",
        "bigmodel": "glm",
        "zhipu": "glm",
        "openai-compatible": "generic",
        "openai_compatible": "generic",
        "custom": "generic",
        "universal": "generic",
    }
    return aliases.get(p, p)


def _strip_last_v1(base_url: str) -> str:
    s = str(base_url or "").strip().rstrip("/")
    if s.endswith("/v1"):
        return s[: -len("/v1")]
    return s


def _resolve_llm_endpoint(
    *,
    provider: str,
    explicit_base_url: str,
    explicit_api_key: str,
    default_base_url: str,
    default_api_key: str,
) -> Tuple[str, str, str]:
    p = _normalize_provider(provider)
    base = str(explicit_base_url or "").strip()
    key = str(explicit_api_key or "").strip()
    resolved = p or "proxy"

    if p in {"", "proxy"}:
        base = base or str(default_base_url or "").strip()
        key = key or str(default_api_key or "").strip()
        resolved = "proxy"
    elif p == "dashscope":
        base = base or str(os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode"))
        key = key or str(os.getenv("DASHSCOPE_API_KEY", "")).strip()
    elif p == "internlm":
        base = base or str(os.getenv("INTERNLM_BASE_URL", "https://chat.intern-ai.org.cn/api/v1"))
        key = key or str(
            os.getenv("INTERNLM_API_KEY")
            or os.getenv("INTERN_API_KEY")
            or os.getenv("INTERNLM_TOKEN")
            or ""
        ).strip()
    elif p == "glm":
        base = base or str(os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"))
        key = key or str(
            os.getenv("GLM_API_KEY")
            or os.getenv("BIGMODEL_API_KEY")
            or os.getenv("ZHIPU_API_KEY")
            or ""
        ).strip()
    elif p == "openai":
        base = base or str(os.getenv("OPENAI_BASE_URL", "https://api.openai.com"))
        key = key or str(os.getenv("OPENAI_API_KEY", "")).strip()
    elif p == "generic":
        base = base or str(os.getenv("AUTOSKILL_GENERIC_LLM_URL", "http://35.220.164.252:3888/v1"))
        key = key or str(os.getenv("AUTOSKILL_GENERIC_API_KEY", "")).strip()
    else:
        # Unknown provider: keep explicit overrides if present, otherwise fallback to proxy.
        base = base or str(default_base_url or "").strip()
        key = key or str(default_api_key or "").strip()
        resolved = f"unknown:{p}"

    base = _strip_last_v1(base)
    return base, key, resolved


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoSkill automatic evolution evaluation")
    parser.add_argument("--mode", default="eval", choices=["eval"])
    parser.add_argument("--eval-strategy", default="evolution", choices=["evolution"])
    parser.add_argument("--base-url", default="http://127.0.0.1:9000")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout-s", type=float, default=25.0)

    parser.add_argument("--eval-runs", type=int, default=32)
    parser.add_argument("--eval-seed", type=int, default=42)
    parser.add_argument("--eval-user-prefix", default="proxy_eval")
    parser.add_argument("--eval-max-train-turns", type=int, default=10)
    parser.add_argument("--eval-stream", action="store_true")
    parser.add_argument("--eval-turn-timeout-s", type=float, default=240.0)
    parser.add_argument("--eval-extraction-timeout-s", type=float, default=360.0)
    parser.add_argument("--eval-poll-interval-s", type=float, default=0.8)
    parser.add_argument("--strict-eval", action="store_true")

    parser.add_argument(
        "--sim-provider",
        default=os.getenv("EVAL_SIM_PROVIDER", ""),
        help="Simulator LLM provider (e.g., proxy|qwen|internlm|glm|openai|generic). Default: proxy.",
    )
    parser.add_argument(
        "--sim-api-key",
        default=os.getenv("EVAL_SIM_API_KEY", ""),
        help="Optional simulator API key override. If empty, use provider env defaults.",
    )
    parser.add_argument(
        "--sim-model",
        default=os.getenv("EVAL_SIM_MODEL", ""),
        help="Optional simulator model override. Default: reuse proxy chat model.",
    )

    parser.add_argument(
        "--judge-provider",
        default=os.getenv("EVAL_JUDGE_PROVIDER", ""),
        help="Judge LLM provider (e.g., proxy|qwen|internlm|glm|openai|generic). Default: proxy.",
    )
    parser.add_argument(
        "--judge-api-key",
        default=os.getenv("EVAL_JUDGE_API_KEY", ""),
        help="Optional judge API key override. If empty, use provider env defaults.",
    )
    parser.add_argument(
        "--judge-model",
        default=os.getenv("EVAL_JUDGE_MODEL", ""),
        help="Optional judge model override. Default: reuse proxy chat model.",
    )
    parser.add_argument("--judge-success-threshold", type=float, default=70.0)
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
    if not model:
        try:
            model = _pick_chat_model(client, preferred="")
        except Exception as e:
            print("[eval] cannot discover model from proxy. Please ensure proxy is running and reachable.")
            print(f"[eval] discovery error: {e}")
            raise SystemExit(1)

    simulator = _build_simulator_client(
        sim_provider=str(args.sim_provider),
        sim_api_key=str(args.sim_api_key),
        sim_model=str(args.sim_model),
        default_base_url=str(args.base_url),
        default_api_key=str(args.api_key),
        default_model=str(model),
        timeout_s=float(args.timeout_s),
    )
    if simulator is None:
        print("[eval] simulator is required for automated LLM-vs-LLM evaluation.")
        raise SystemExit(1)
    sim_model_show = str(getattr(simulator, "model", "") or str(model))
    sim_provider_show = _normalize_provider(str(args.sim_provider or "")) or "proxy"
    print(f"[eval] simulator: enabled provider={sim_provider_show} model={sim_model_show}")

    judge_llm = _build_judge_client(
        judge_provider=str(args.judge_provider),
        judge_api_key=str(args.judge_api_key),
        judge_model=str(args.judge_model),
        default_base_url=str(args.base_url),
        default_api_key=str(args.api_key),
        default_model=str(model),
        timeout_s=float(args.timeout_s),
    )
    if judge_llm is None:
        print("[eval] judge model is required for automated LLM-vs-LLM evaluation.")
        raise SystemExit(1)
    judge_model_show = str(getattr(judge_llm, "model", "") or str(model))
    judge_provider_show = _normalize_provider(str(args.judge_provider or "")) or "proxy"
    print(
        f"[eval] judge: enabled provider={judge_provider_show} model={judge_model_show} "
        f"threshold={float(args.judge_success_threshold):.1f}"
    )

    eval_result = run_eval_evolution(
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
        judge_success_threshold=float(args.judge_success_threshold),
        max_train_turns=int(args.eval_max_train_turns),
        verbose=bool(args.verbose),
    )

    report: Dict[str, Any] = {
        "meta": {
            "base_url": str(args.base_url),
            "mode": "eval",
            "eval_strategy": "evolution",
            "model": str(model),
            "time_unix": int(time.time()),
        },
        "evaluation": eval_result,
    }

    summary = eval_result.get("summary") if isinstance(eval_result, dict) else {}
    metrics = summary.get("metrics") if isinstance(summary, dict) else {}
    total_cases = int(summary.get("total_cases") or 0)
    ok_cases = int(summary.get("ok_cases") or 0)
    print("\n[eval] summary:")
    print(
        json.dumps(
            {
                "total_cases": total_cases,
                "ok_cases": ok_cases,
                "metrics": metrics,
                "coverage": summary.get("coverage"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    overall_ok = True
    if bool(args.strict_eval):
        strict_ok = True
        sr_before = metrics.get("sr_before")
        sr_after = metrics.get("sr_after")
        score_before = metrics.get("avg_score_before")
        score_after = metrics.get("avg_score_after")
        if isinstance(sr_after, (int, float)) and isinstance(sr_before, (int, float)):
            if float(sr_after) < float(sr_before):
                strict_ok = False
                print(f"[eval][strict] SR regressed: after={float(sr_after):.3f} < before={float(sr_before):.3f}")
        if isinstance(score_after, (int, float)) and isinstance(score_before, (int, float)):
            if float(score_after) < float(score_before):
                strict_ok = False
                print(
                    f"[eval][strict] score regressed: after={float(score_after):.2f} < before={float(score_before):.2f}"
                )
        if not strict_ok:
            overall_ok = False
        else:
            print(
                "[eval][strict] passed "
                f"(sr_before={sr_before}, sr_after={sr_after}, "
                f"avg_score_before={score_before}, avg_score_after={score_after})"
            )

    try:
        report_path, analysis_path = _persist_eval_outputs(
            report=report,
            eval_result=eval_result if isinstance(eval_result, dict) else {},
            report_json_arg=str(args.report_json or ""),
        )
        print(f"\nReport saved: {report_path}")
        print(f"Case analysis saved: {analysis_path}")
    except Exception as e:
        print(f"\nFailed to save evaluation outputs: {e}")
        overall_ok = False

    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
