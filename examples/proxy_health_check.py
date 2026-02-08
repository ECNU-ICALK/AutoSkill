"""
AutoSkill OpenAI-compatible proxy health check.

Usage:
  python3 -m examples.proxy_health_check --base-url http://127.0.0.1:9000

Optional:
  export AUTOSKILL_PROXY_API_KEY="your_key"
  python3 -m examples.proxy_health_check --api-key "$AUTOSKILL_PROXY_API_KEY"
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


class ProxyClient:
    def __init__(self, *, base_url: str, api_key: str, timeout_s: float) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.api_key = str(api_key or "").strip()
        self.timeout_s = float(timeout_s)

    def _headers(self, *, json_body: bool = True) -> Dict[str, str]:
        out: Dict[str, str] = {"Accept": "application/json"}
        if json_body:
            out["Content-Type"] = "application/json"
        if self.api_key:
            out["Authorization"] = f"Bearer {self.api_key}"
        return out

    def request_json(self, *, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            method=str(method).upper(),
            data=data,
            headers=self._headers(json_body=(payload is not None or method.upper() != "GET")),
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
            raise RuntimeError(f"Invalid JSON from {method} {path}: {body[:300]}") from e
        if not isinstance(obj, dict):
            raise RuntimeError(f"Expected JSON object from {method} {path}, got: {type(obj).__name__}")
        return obj

    def request_stream_events(self, *, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            method="POST",
            data=data,
            headers=self._headers(json_body=True),
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                done = False
                chunk_count = 0
                error_msg = ""
                saw_data_line = False
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
                    err = obj.get("error")
                    if isinstance(err, dict):
                        msg = str(err.get("message") or "").strip()
                        if msg:
                            error_msg = msg
                return {
                    "done": bool(done),
                    "chunk_count": int(chunk_count),
                    "error": str(error_msg),
                    "saw_data_line": bool(saw_data_line),
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


def _run_check(name: str, fn) -> CheckResult:
    try:
        detail = str(fn() or "ok")
        return CheckResult(name=name, ok=True, detail=detail)
    except Exception as e:
        return CheckResult(name=name, ok=False, detail=str(e))


def _check_health(client: ProxyClient) -> str:
    obj = client.request_json(method="GET", path="/health")
    if not bool(obj.get("ok")):
        raise RuntimeError(f"unexpected health payload: {obj}")
    return "GET /health ok=true"


def _pick_chat_model(client: ProxyClient, *, preferred: str = "") -> str:
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


def _check_models(client: ProxyClient) -> str:
    obj = client.request_json(method="GET", path="/v1/models")
    if str(obj.get("object") or "") != "list":
        raise RuntimeError(f"unexpected object: {obj.get('object')}")
    data = obj.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("models list is empty")
    first = data[0] if isinstance(data[0], dict) else {}
    model = str(first.get("id") or "").strip() or "<empty>"
    return f"GET /v1/models count={len(data)} first={model}"


def _check_capabilities(client: ProxyClient) -> str:
    obj = client.request_json(method="GET", path="/v1/autoskill/capabilities")
    if str(obj.get("object") or "") != "autoskill.capabilities":
        raise RuntimeError(f"unexpected object: {obj.get('object')}")
    return "GET /v1/autoskill/capabilities ok"


def _chat_payload(user_id: str, *, stream: bool, model: str) -> Dict[str, Any]:
    return {
        "model": str(model),
        "stream": bool(stream),
        "temperature": 0.0,
        "max_tokens": 64,
        "user": user_id,
        "messages": [
            {"role": "user", "content": "Reply with one short sentence to confirm proxy health."}
        ],
    }


def _check_chat_non_stream(client: ProxyClient, *, user_id: str, model: str) -> str:
    obj = client.request_json(
        method="POST",
        path="/v1/chat/completions",
        payload=_chat_payload(user_id, stream=False, model=model),
    )
    choices = obj.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("no choices in response")
    msg = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = str((msg or {}).get("content") or "").strip()
    if not content:
        raise RuntimeError("assistant content is empty")
    autoskill = obj.get("autoskill")
    if not isinstance(autoskill, dict):
        raise RuntimeError("missing autoskill diagnostics")
    return f"POST /v1/chat/completions non-stream ok model={model}"


def _check_chat_stream(client: ProxyClient, *, user_id: str, model: str) -> str:
    result = client.request_stream_events(
        path="/v1/chat/completions",
        payload=_chat_payload(user_id, stream=True, model=model),
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


def _check_retrieval_preview(client: ProxyClient, *, user_id: str) -> str:
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


def _check_extraction(client: ProxyClient, *, user_id: str, timeout_s: float) -> str:
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

    terminal = {"completed", "failed"}
    deadline = time.time() + float(timeout_s)
    last = data
    while time.time() < deadline:
        cur = client.request_json(method="GET", path=f"/v1/autoskill/extractions/{job_id}")
        cur_data = cur.get("data")
        if isinstance(cur_data, dict):
            last = cur_data
        status = str(last.get("status") or "").strip().lower()
        if status in terminal:
            upserted = last.get("upserted")
            count = len(upserted) if isinstance(upserted, list) else 0
            return f"extraction status={status} upserted={count}"
        time.sleep(0.4)

    raise RuntimeError(f"extraction did not finish within {timeout_s}s, last={last}")


def _check_embeddings(client: ProxyClient) -> str:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Health-check AutoSkill reverse proxy")
    parser.add_argument("--base-url", default="http://127.0.0.1:9000")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--user-id", default="proxy_test_user")
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout-s", type=float, default=20.0)
    parser.add_argument("--skip-embeddings", action="store_true")
    args = parser.parse_args()

    client = ProxyClient(
        base_url=str(args.base_url),
        api_key=str(args.api_key),
        timeout_s=float(args.timeout_s),
    )
    model = _pick_chat_model(client, preferred=str(args.model))

    checks = [
        ("health", lambda: _check_health(client)),
        ("models", lambda: _check_models(client)),
        ("capabilities", lambda: _check_capabilities(client)),
        ("chat_non_stream", lambda: _check_chat_non_stream(client, user_id=str(args.user_id), model=model)),
        ("chat_stream", lambda: _check_chat_stream(client, user_id=str(args.user_id), model=model)),
        ("retrieval_preview", lambda: _check_retrieval_preview(client, user_id=str(args.user_id))),
        (
            "extraction",
            lambda: _check_extraction(client, user_id=str(args.user_id), timeout_s=float(args.timeout_s)),
        ),
    ]
    if not bool(args.skip_embeddings):
        checks.append(("embeddings", lambda: _check_embeddings(client)))

    results = [_run_check(name, fn) for name, fn in checks]

    ok_count = 0
    for r in results:
        if r.ok:
            ok_count += 1
            print(f"[PASS] {r.name}: {r.detail}")
        else:
            print(f"[FAIL] {r.name}: {r.detail}")

    total = len(results)
    if ok_count == total:
        print(f"\nAll checks passed ({ok_count}/{total}). Proxy service is healthy.")
        return

    print(f"\nChecks failed ({ok_count}/{total} passed).")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
