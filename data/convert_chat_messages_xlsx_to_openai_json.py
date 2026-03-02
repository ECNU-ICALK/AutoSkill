"""Convert `chat_messages_export.csv` into OpenAI conversation JSON files.

Core rule implemented:
- Each row id is in form: `id = chat_id + "-" + turn_id`
- `parent_id` points to the previous turn's `turn_id`
- Rebuild conversation chains by linking `turn_id <- parent_id`

Output layout (one file per session):
`<output_dir>/<user_id>/<chat_id>.json`

Payload format:
{
  "model": "...",
  "messages": [{"role": "...", "content": "..."}, ...]
}

Usage:
  python3 data/convert_chat_messages_xlsx_to_openai_json.py \
    --input data/chat_messages_export.csv \
    --output-dir data/chat_messages_openai_by_user
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


@dataclass
class Msg:
    user_id: str
    chat_id: str
    turn_id: str
    parent_id: str
    role: str
    content: str
    model_id: str
    created_at: int
    updated_at: int
    row_index: int


def _build_parser() -> argparse.ArgumentParser:
    """Run build parser."""
    p = argparse.ArgumentParser(description="Convert chat_messages export csv to OpenAI JSON conversations.")
    p.add_argument(
        "--input",
        default="data/chat_messages_export.csv",
        help="Input csv file path.",
    )
    p.add_argument(
        "--output-dir",
        default="data/chat_messages_openai_by_user",
        help="Output directory. Layout: output_dir/user_id/chat_id.json",
    )
    p.add_argument(
        "--export-mode",
        choices=["longest", "all-paths"],
        default="longest",
        help="`longest`: one conversation per session; `all-paths`: export every root-to-leaf path.",
    )
    p.add_argument(
        "--min-messages",
        type=int,
        default=2,
        help="Only export conversations with at least this many messages.",
    )
    p.add_argument(
        "--max-sessions",
        type=int,
        default=0,
        help="Debug limit. 0 means all sessions.",
    )
    p.add_argument(
        "--progress-every",
        type=int,
        default=100000,
        help="Print progress every N input rows.",
    )
    return p


def _normalize_text(v: Any) -> str:
    """Run normalize text."""
    if v is None:
        return ""
    return str(v)


def _clean_text(v: Any) -> str:
    """Run clean text."""
    return _normalize_text(v).strip()


def _to_int(v: Any) -> int:
    """Run to int."""
    s = _clean_text(v)
    if not s:
        return 0
    try:
        return int(float(s))
    except Exception:
        return 0


def _safe_filename(s: str) -> str:
    """Run safe filename."""
    out = re.sub(r"[^A-Za-z0-9._-]+", "_", str(s or "").strip())
    return out or "unknown"


def _normalize_field_name(name: Any) -> str:
    """Run normalize field name."""
    return _normalize_text(name).replace("\ufeff", "").strip()


def _set_csv_field_limit_max() -> None:
    """Run set csv field limit max."""
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit = limit // 10


def _iter_records(path: Path) -> Iterator[Dict[str, str]]:
    """Run iter records."""
    _set_csv_field_limit_max()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return
        fieldnames = [_normalize_field_name(x) for x in reader.fieldnames]
        reader.fieldnames = fieldnames
        for row in reader:
            rec: Dict[str, str] = {}
            for k, v in row.items():
                if k is None:
                    continue
                rec[_normalize_field_name(k)] = _normalize_text(v)
            yield rec


def _infer_turn_id(chat_id: str, row_id: str) -> str:
    """Run infer turn id."""
    rid = _clean_text(row_id)
    prefix = f"{chat_id}-"
    if rid.startswith(prefix):
        return rid[len(prefix) :]
    return rid


def _record_to_msg(rec: Dict[str, str], row_index: int) -> Optional[Msg]:
    """Run record to msg."""
    user_id = _clean_text(rec.get("user_id")) or "unknown_user"
    chat_id = _clean_text(rec.get("chat_id"))
    row_id = _clean_text(rec.get("id"))
    role = _clean_text(rec.get("role")).lower()
    parent_id = _clean_text(rec.get("parent_id"))
    content = _normalize_text(rec.get("content"))
    if not content.strip():
        # Some exports place assistant text in `output`.
        content = _normalize_text(rec.get("output"))
    content = content.strip()

    if not chat_id or not row_id or not content:
        return None
    if role not in {"system", "user", "assistant", "tool"}:
        return None

    turn_id = _infer_turn_id(chat_id, row_id)
    if not turn_id:
        return None

    return Msg(
        user_id=user_id,
        chat_id=chat_id,
        turn_id=turn_id,
        parent_id=parent_id,
        role=role,
        content=content,
        model_id=_clean_text(rec.get("model_id")),
        created_at=_to_int(rec.get("created_at")),
        updated_at=_to_int(rec.get("updated_at")),
        row_index=row_index,
    )


def _dedupe_turns(rows: List[Msg]) -> Dict[str, Msg]:
    """Run dedupe turns."""
    by_turn: Dict[str, Msg] = {}
    for m in rows:
        prev = by_turn.get(m.turn_id)
        if prev is None:
            by_turn[m.turn_id] = m
            continue
        prev_key = (prev.updated_at, prev.created_at, prev.row_index)
        cur_key = (m.updated_at, m.created_at, m.row_index)
        if cur_key >= prev_key:
            by_turn[m.turn_id] = m
    return by_turn


def _build_paths(rows: List[Msg]) -> List[List[Msg]]:
    """Run build paths."""
    by_turn = _dedupe_turns(rows)
    if not by_turn:
        return []

    children: Dict[str, List[str]] = defaultdict(list)
    roots: List[str] = []

    for tid, msg in by_turn.items():
        pid = _clean_text(msg.parent_id)
        if pid and pid in by_turn:
            children[pid].append(tid)
        else:
            roots.append(tid)

    def _sort_key(tid: str) -> Tuple[int, int, str]:
        """Run sort key."""
        m = by_turn[tid]
        return (m.created_at, m.row_index, tid)

    for pid in list(children.keys()):
        children[pid].sort(key=_sort_key)
    roots = sorted(set(roots), key=_sort_key)

    if not roots:
        roots = [min(by_turn.keys(), key=_sort_key)]

    paths: List[List[Msg]] = []

    def dfs(tid: str, stack: List[str], seen: set[str]) -> None:
        """Run dfs."""
        if tid in seen:
            paths.append([by_turn[x] for x in stack + [tid]])
            return
        stack2 = stack + [tid]
        seen2 = set(seen)
        seen2.add(tid)
        kids = children.get(tid, [])
        if not kids:
            paths.append([by_turn[x] for x in stack2])
            return
        for kid in kids:
            dfs(kid, stack2, seen2)

    for r in roots:
        dfs(r, [], set())

    return paths


def _choose_longest_path(paths: List[List[Msg]]) -> List[Msg]:
    """Run choose longest path."""
    if not paths:
        return []

    def key_fn(p: List[Msg]) -> Tuple[int, int, int]:
        """Run key fn."""
        last = p[-1] if p else None
        ts = (last.updated_at if last else 0, last.created_at if last else 0)
        return (len(p), ts[0], ts[1])

    return max(paths, key=key_fn)


def _path_to_openai_payload(path: List[Msg]) -> Dict[str, Any]:
    """Run path to openai payload."""
    messages = [{"role": m.role, "content": m.content} for m in path]
    models = [m.model_id for m in path if _clean_text(m.model_id)]
    payload: Dict[str, Any] = {"messages": messages}
    if models:
        payload["model"] = Counter(models).most_common(1)[0][0]
    return payload


def main() -> None:
    """Run main."""
    args = _build_parser().parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        raise SystemExit(f"Input file not found: {input_path}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    groups: Dict[Tuple[str, str], List[Msg]] = defaultdict(list)
    total_rows = 0
    valid_rows = 0

    for idx, rec in enumerate(_iter_records(input_path), start=2):
        total_rows += 1
        msg = _record_to_msg(rec, row_index=idx)
        if msg is None:
            continue
        groups[(msg.user_id, msg.chat_id)].append(msg)
        valid_rows += 1
        if args.progress_every > 0 and total_rows % args.progress_every == 0:
            print(
                f"rows={total_rows:,}, valid={valid_rows:,}, "
                f"sessions={len(groups):,}, users={len({u for u, _ in groups.keys()}):,}"
            )

    session_keys = sorted(groups.keys())
    if args.max_sessions > 0:
        session_keys = session_keys[: int(args.max_sessions)]

    exported_sessions = 0
    exported_paths = 0
    skipped_short = 0

    for user_id, chat_id in session_keys:
        paths = _build_paths(groups[(user_id, chat_id)])
        if not paths:
            continue

        if args.export_mode == "longest":
            use_paths = [_choose_longest_path(paths)]
        else:
            use_paths = paths

        user_dir = out_dir / _safe_filename(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        base = _safe_filename(chat_id)

        for i, path in enumerate(use_paths, start=1):
            if len(path) < max(1, int(args.min_messages)):
                skipped_short += 1
                continue
            payload = _path_to_openai_payload(path)
            if args.export_mode == "all-paths":
                fname = f"{base}__p{i:03d}.json"
            else:
                fname = f"{base}.json"
            (user_dir / fname).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            exported_paths += 1
        exported_sessions += 1

    print("Done.")
    print(f"input={input_path}")
    print(f"output_dir={out_dir}")
    print(f"total_rows={total_rows:,}")
    print(f"valid_rows={valid_rows:,}")
    print(f"users_seen={len({u for u, _ in groups.keys()}):,}")
    print(f"sessions_seen={len(groups):,}")
    print(f"sessions_processed={len(session_keys):,}")
    print(f"conversations_exported={exported_paths:,}")
    print(f"skipped_short={skipped_short:,}")


if __name__ == "__main__":
    main()
