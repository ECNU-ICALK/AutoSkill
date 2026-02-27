"""
Offline document extraction.

Extracts reusable skills from books/papers/manuals by chunking document text and
feeding chunks into the existing AutoSkill ingest pipeline.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, List, Optional

from autoskill import AutoSkill, AutoSkillConfig
from .file_loader import data_to_text_unit, load_file_units
from .prompt_runtime import activate_offline_prompt_runtime


def extract_from_doc(
    *,
    sdk: AutoSkill,
    user_id: str,
    data: Optional[Any] = None,
    file_path: str = "",
    title: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
    continue_on_error: bool = True,
    max_chars_per_chunk: int = 6000,
    overlap_chars: int = 300,
) -> Dict[str, Any]:
    """
    Runs offline extraction from heterogeneous offline files/directories.
    """

    abs_input = ""
    units: List[Dict[str, str]] = []
    if data is not None:
        unit_title = str(title or "").strip() or "inline_data"
        units = [data_to_text_unit(data, title=unit_title)]
    elif str(file_path or "").strip():
        units, abs_input = load_file_units(str(file_path))
    else:
        raise ValueError("extract_from_doc requires data or file_path")
    if not units:
        return {
            "total_units": 0,
            "total_chunks": 0,
            "processed_chunks": 0,
            "failed_chunks": 0,
            "upserted_count": 0,
            "skills": [],
            "errors": [],
            "source_file": abs_input or None,
        }

    if str(title or "").strip():
        default_title = str(title).strip()
    elif abs_input:
        default_title = os.path.basename(abs_input)
    else:
        default_title = "document_corpus"

    max_chars = max(800, int(max_chars_per_chunk or 6000))
    overlap = max(0, min(max_chars // 2, int(overlap_chars or 0)))
    base_md = dict(metadata or {})
    base_md.setdefault("channel", "offline_extract_from_doc")
    base_md.setdefault("source_type", "document")
    if abs_input:
        base_md.setdefault("source_file", abs_input)

    processed = 0
    failed = 0
    errors: List[Dict[str, Any]] = []
    upserted_by_id: Dict[str, Any] = {}
    total_chunks = 0

    with activate_offline_prompt_runtime(sdk=sdk, channel="offline_extract_from_doc"):
        for unit_idx, unit in enumerate(units):
            unit_title = str(unit.get("title") or "").strip() or default_title
            unit_text = str(unit.get("text") or "").strip()
            unit_source_file = str(unit.get("source_file") or "").strip()
            if not unit_text:
                continue
            chunks = _split_text(unit_text, max_chars=max_chars, overlap=overlap)
            total_chunks += len(chunks)
            for chunk_idx, chunk in enumerate(chunks):
                msg = _build_doc_message(title=unit_title, chunk=chunk)
                md = dict(base_md)
                md["unit_index"] = int(unit_idx)
                md["chunk_index"] = int(chunk_idx)
                md["unit_title"] = unit_title
                if unit_source_file:
                    md["source_file"] = unit_source_file
                try:
                    updated = sdk.ingest(
                        user_id=str(user_id or "").strip() or "u1",
                        messages=[{"role": "user", "content": msg}],
                        events=None,
                        metadata=md,
                        hint=(str(hint).strip() if hint and str(hint).strip() else None),
                    )
                    processed += 1
                    for s in (updated or []):
                        sid = str(getattr(s, "id", "") or "")
                        if sid:
                            upserted_by_id[sid] = s
                except Exception as e:
                    failed += 1
                    errors.append(
                        {
                            "unit_index": unit_idx,
                            "chunk_index": chunk_idx,
                            "error": str(e),
                        }
                    )
                    if not continue_on_error:
                        raise

    return {
        "total_units": len(units),
        "total_chunks": total_chunks,
        "processed_chunks": processed,
        "failed_chunks": failed,
        "upserted_count": len(upserted_by_id),
        "skills": [_skill_to_plain_dict(s) for s in upserted_by_id.values()],
        "errors": errors,
        "source_file": abs_input or None,
    }


def _build_doc_message(*, title: str, chunk: str) -> str:
    return (
        "Document source for offline skill learning.\n"
        f"Title: {title}\n"
        "Extract reusable capability/policy/workflow skills from this excerpt.\n"
        "Document excerpt:\n"
        f"{chunk}"
    )


def _skill_to_plain_dict(skill: Any) -> Dict[str, Any]:
    try:
        examples = []
        for e in list(getattr(skill, "examples", []) or []):
            examples.append(
                {
                    "input": str(getattr(e, "input", "") or ""),
                    "output": (str(getattr(e, "output", "") or "") or None),
                    "notes": (str(getattr(e, "notes", "") or "") or None),
                }
            )
        return {
            "id": str(getattr(skill, "id", "") or ""),
            "name": str(getattr(skill, "name", "") or ""),
            "description": str(getattr(skill, "description", "") or ""),
            "version": str(getattr(skill, "version", "") or ""),
            "triggers": list(getattr(skill, "triggers", []) or []),
            "tags": list(getattr(skill, "tags", []) or []),
            "examples": examples,
        }
    except Exception:
        return {"id": "", "name": "", "description": "", "version": ""}


def _split_text(text: str, *, max_chars: int, overlap: int) -> List[str]:
    """
    Paragraph-aware chunking with character overlap.
    """

    src = str(text or "").strip()
    if not src:
        return []
    if len(src) <= max_chars:
        return [src]

    paras = [p.strip() for p in src.split("\n\n") if p.strip()]
    if not paras:
        paras = [src]

    chunks: List[str] = []
    cur = ""
    for p in paras:
        if not cur:
            cur = p
            continue
        nxt = f"{cur}\n\n{p}"
        if len(nxt) <= max_chars:
            cur = nxt
            continue
        chunks.append(cur)
        if overlap > 0:
            tail = cur[-overlap:]
            cur = f"{tail}\n\n{p}"
        else:
            cur = p
        if len(cur) > max_chars:
            # Hard-split extremely long paragraph.
            for i in range(0, len(cur), max_chars):
                part = cur[i : i + max_chars].strip()
                if part:
                    chunks.append(part)
            cur = ""
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def _env(name: str, default: str = "") -> str:
    val = os.getenv(name)
    return val if val is not None and val.strip() else default


def _build_llm_config(args: argparse.Namespace) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {"provider": str(args.llm_provider or "mock").strip()}
    if str(args.llm_model or "").strip():
        cfg["model"] = str(args.llm_model).strip()
    if str(args.llm_base_url or "").strip():
        cfg["base_url"] = str(args.llm_base_url).strip()
    if str(args.llm_api_key or "").strip():
        cfg["api_key"] = str(args.llm_api_key).strip()
    if str(args.auth_mode or "").strip():
        cfg["auth_mode"] = str(args.auth_mode).strip()
    return cfg


def _build_sdk_from_args(args: argparse.Namespace) -> AutoSkill:
    llm_cfg = _build_llm_config(args)
    store_cfg: Dict[str, Any] = {"provider": "local"}
    if str(args.store_path or "").strip():
        store_cfg["path"] = str(args.store_path).strip()
    return AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings={"provider": "hashing", "dims": 256},
            store=store_cfg,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract skills from offline document corpora.")
    parser.add_argument("--file", required=True, help="Path to a file or directory.")
    parser.add_argument("--user-id", default="u1", help="Target user id.")
    parser.add_argument("--title", default="", help="Optional document title override.")
    parser.add_argument("--hint", default="", help="Optional extraction hint.")
    parser.add_argument("--max-chars-per-chunk", type=int, default=6000)
    parser.add_argument("--overlap-chars", type=int, default=300)
    parser.add_argument(
        "--llm-provider",
        default=_env("AUTOSKILL_LLM_PROVIDER", "mock"),
        help="mock|generic|glm|internlm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=_env("AUTOSKILL_LLM_MODEL", ""))
    parser.add_argument("--llm-base-url", default=_env("AUTOSKILL_LLM_BASE_URL", ""))
    parser.add_argument("--llm-api-key", default=_env("AUTOSKILL_LLM_API_KEY", ""))
    parser.add_argument("--auth-mode", default=_env("AUTOSKILL_LLM_AUTH_MODE", ""))
    parser.add_argument("--store-path", default=_env("AUTOSKILL_STORE_PATH", ""))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sdk = _build_sdk_from_args(args)
    result = extract_from_doc(
        sdk=sdk,
        user_id=str(args.user_id).strip() or "u1",
        file_path=str(args.file or ""),
        title=str(args.title or ""),
        hint=(str(args.hint).strip() or None),
        continue_on_error=True,
        max_chars_per_chunk=int(args.max_chars_per_chunk or 6000),
        overlap_chars=int(args.overlap_chars or 0),
        metadata={"channel": "offline_extract_from_doc"},
    )
    print("Offline document extraction completed.")
    print(
        f"units={result.get('total_units', 0)} "
        f"chunks={result.get('total_chunks', 0)} "
        f"processed={result.get('processed_chunks', 0)} "
        f"failed={result.get('failed_chunks', 0)} "
        f"upserted={result.get('upserted_count', 0)}"
    )
    for i, s in enumerate(list(result.get("skills") or []), start=1):
        print(f"{i}. {s.get('name', '')} ({s.get('version', '')})")
    errors = list(result.get("errors") or [])
    if errors:
        print("Errors:")
        for e in errors[:20]:
            print(f"- unit#{e.get('unit_index')} chunk#{e.get('chunk_index')}: {e.get('error')}")


if __name__ == "__main__":
    main()
