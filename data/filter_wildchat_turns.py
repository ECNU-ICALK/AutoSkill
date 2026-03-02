"""Download WildChat-1M and filter conversations with turns > N.

Example:
  python3 -m examples.filter_wildchat_turns \
    --min-turns 5 \
    --output data/wildchat_turns_gt5.jsonl
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Dict, Optional


def _infer_turns(example: Dict[str, Any]) -> Optional[int]:
    """Infer conversation turn count from common field names."""
    for key in ("turns", "turn"):
        value = example.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)

    for key in ("conversation", "messages", "dialogue", "chat"):
        value = example.get(key)
        if isinstance(value, list):
            return len(value)

    return None


def _build_parser() -> argparse.ArgumentParser:
    """Run build parser."""
    parser = argparse.ArgumentParser(
        description="Download Hugging Face dataset and keep rows with turns > min_turns."
    )
    parser.add_argument(
        "--dataset",
        default="allenai/WildChat-1M",
        help="Hugging Face dataset id (default: allenai/WildChat-1M)",
    )
    parser.add_argument("--split", default="train", help="Dataset split (default: train)")
    parser.add_argument(
        "--min-turns",
        type=int,
        default=5,
        help="Keep rows where turns > min_turns (default: 5)",
    )
    parser.add_argument(
        "--output",
        default="data/wildchat_turns_gt5.jsonl",
        help="Output JSONL file path",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Optional cache dir for Hugging Face datasets",
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Use streaming mode (recommended for large datasets)",
    )
    parser.add_argument(
        "--num-proc",
        type=int,
        default=4,
        help="Parallel workers for non-streaming filter (default: 4)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Optional cap for processed rows in streaming mode; 0 means no limit",
    )
    parser.add_argument(
        "--remote-prefilter",
        action="store_true",
        help=(
            "Try remote parquet prefilter on `turn > min_turns` before streaming rows. "
            "Can reduce network traffic when backend supports predicate pushdown."
        ),
    )
    return parser


def _json_default(value: Any) -> str:
    """Serialize non-JSON-native values in dataset rows."""
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    return str(value)


def _load_streaming_dataset(args: argparse.Namespace):
    """Run load streaming dataset."""
    from datasets import load_dataset

    if args.remote_prefilter:
        try:
            from huggingface_hub import hf_hub_url, list_repo_files

            repo_files = list_repo_files(args.dataset, repo_type="dataset")
            parquet_files = sorted(f for f in repo_files if f.endswith(".parquet"))
            if parquet_files:
                urls = [
                    hf_hub_url(repo_id=args.dataset, repo_type="dataset", filename=f)
                    for f in parquet_files
                ]
                print(
                    f"Using remote prefilter: scan {len(urls)} parquet files with turn > {args.min_turns}"
                )
                return load_dataset(
                    "parquet",
                    data_files={args.split: urls},
                    split=args.split,
                    cache_dir=args.cache_dir,
                    streaming=True,
                    filters=[("turn", ">", args.min_turns)],
                )
        except Exception as e:
            print(f"Remote prefilter unavailable, fallback to normal streaming: {e}")

    return load_dataset(
        args.dataset,
        split=args.split,
        cache_dir=args.cache_dir,
        streaming=True,
    )


def _run_streaming(args: argparse.Namespace) -> None:
    """Run run streaming."""
    ds = _load_streaming_dataset(args)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    kept = 0
    with output_path.open("w", encoding="utf-8") as f:
        for row in ds:
            total += 1
            turns = _infer_turns(row)
            if turns is not None and turns > args.min_turns:
                kept += 1
                f.write(json.dumps(row, ensure_ascii=False, default=_json_default) + "\n")

            if total % 10000 == 0:
                print(f"processed={total:,}, kept={kept:,}")

            if args.max_rows > 0 and total >= args.max_rows:
                break

    print(f"Done. total={total:,}, kept={kept:,}, output={output_path}")


def _run_non_streaming(args: argparse.Namespace) -> None:
    """Run run non streaming."""
    from datasets import load_dataset

    ds = load_dataset(
        args.dataset,
        split=args.split,
        cache_dir=args.cache_dir,
        streaming=False,
    )

    filtered = ds.filter(
        lambda row: (_infer_turns(row) or -1) > args.min_turns,
        num_proc=max(1, args.num_proc),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_json(str(output_path), orient="records", lines=True, force_ascii=False)
    print(f"Done. total={len(ds):,}, kept={len(filtered):,}, output={output_path}")


def main() -> None:
    """Run main."""
    args = _build_parser().parse_args()

    if args.min_turns < 0:
        raise SystemExit("--min-turns must be >= 0")

    try:
        import datasets  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "Missing dependency: datasets. Install with: python3 -m pip install datasets"
        ) from e

    if args.streaming:
        _run_streaming(args)
    else:
        _run_non_streaming(args)


if __name__ == "__main__":
    main()
