"""Filter local WildChat JSONL by turn threshold and language.

Example:
  python3 data/filter_wildchat_chinese_turns.py \
    --input data/wildchat_turns_gt5.jsonl \
    --min-turn 10 \
    --language chinese \
    --output data/wildchat_turn_gt10_chinese.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional


def _infer_turn(record: Dict[str, Any]) -> Optional[int]:
    """Run infer turn."""
    value = record.get("turn")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)

    conversation = record.get("conversation")
    if isinstance(conversation, list):
        # WildChat stores user+assistant messages, so turn ~= message_count // 2.
        return len(conversation) // 2

    return None


def _normalize_language(value: Any) -> str:
    """Run normalize language."""
    return str(value or "").strip().lower()


def _normalize_text(value: Any) -> str:
    """Run normalize text."""
    return str(value or "").strip().lower()


def _project_conversation(conversation: Any) -> list[Dict[str, Any]]:
    """Run project conversation."""
    if not isinstance(conversation, list):
        return []

    projected: list[Dict[str, Any]] = []
    for item in conversation:
        if not isinstance(item, dict):
            continue
        projected.append(
            {
                "content": item.get("content"),
                "language": item.get("language"),
                "role": item.get("role"),
            }
        )
    return projected


def _project_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Run project record."""
    return {
        "conversation_hash": record.get("conversation_hash"),
        "model": record.get("model"),
        "conversation": _project_conversation(record.get("conversation")),
    }


def _build_parser() -> argparse.ArgumentParser:
    """Run build parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Read local JSONL and keep rows where turn > min-turn and language matches."
        )
    )
    parser.add_argument(
        "--input",
        default="data/wildchat_turns_gt5.jsonl",
        help="Input JSONL path",
    )
    parser.add_argument(
        "--output",
        default="data/wildchat_turn_gt10_chinese.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument(
        "--min-turn",
        type=int,
        default=10,
        help="Keep rows where turn > min-turn (default: 10)",
    )
    parser.add_argument(
        "--language",
        default="chinese",
        help="Target language (case-insensitive, default: chinese)",
    )
    parser.add_argument(
        "--model",
        default="",
        help=(
            "Optional model keyword filter (case-insensitive substring match). "
            "Example: gpt-4o"
        ),
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=5000,
        help="Print progress every N rows (default: 5000)",
    )
    return parser


def main() -> None:
    """Run main."""
    args = _build_parser().parse_args()

    if args.min_turn < 0:
        raise SystemExit("--min-turn must be >= 0")

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    target_language = _normalize_language(args.language)
    target_model = _normalize_text(args.model)

    total = 0
    kept = 0
    bad_json = 0
    missing_turn = 0

    with input_path.open("r", encoding="utf-8") as src, output_path.open(
        "w", encoding="utf-8"
    ) as dst:
        for line in src:
            total += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                bad_json += 1
                continue

            turn = _infer_turn(record)
            if turn is None:
                missing_turn += 1
                continue

            language = _normalize_language(record.get("language"))
            model = _normalize_text(record.get("model"))
            model_ok = (not target_model) or (target_model in model)
            if turn > args.min_turn and language == target_language and model_ok:
                kept += 1
                dst.write(json.dumps(_project_record(record), ensure_ascii=False) + "\n")

            if args.progress_every > 0 and total % args.progress_every == 0:
                print(f"processed={total:,}, kept={kept:,}")

    print(
        "Done. "
        f"total={total:,}, kept={kept:,}, bad_json={bad_json:,}, "
        f"missing_turn={missing_turn:,}, output={output_path}"
    )


if __name__ == "__main__":
    main()
