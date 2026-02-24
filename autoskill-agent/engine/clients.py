from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from engine.core import parse_json_from_text


class OpenAICompatTeacher:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_s: float = 90.0,
        name: str = "llm",
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.api_key = str(api_key or "")
        self.model = str(model or "")
        self.timeout_s = float(timeout_s)
        self.name = str(name or "llm")

    def complete_text(self, *, system: str, user: str, temperature: float = 0.0) -> Optional[str]:
        if not self.base_url or not self.model:
            return None
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": float(temperature),
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(
            url=url,
            method="POST",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", errors="replace")
            except Exception:
                detail = str(e)
            print(f"[autoskill-agent] {self.name} teacher HTTP {e.code}: {detail}")
            return None
        except Exception as e:
            print(f"[autoskill-agent] {self.name} teacher request failed: {e}")
            return None

        try:
            obj = json.loads(raw)
        except Exception:
            print(f"[autoskill-agent] {self.name} teacher returned non-json response body.")
            return None
        if not isinstance(obj, dict):
            return None
        choices = obj.get("choices")
        if not isinstance(choices, list) or not choices:
            return None
        first = choices[0] if isinstance(choices[0], dict) else {}
        msg = first.get("message")
        if not isinstance(msg, dict):
            return None
        content = self._extract_message_text(msg)
        return content if content.strip() else None

    def complete_json(self, *, system: str, user: str, temperature: float = 0.0) -> Optional[Dict[str, Any]]:
        text = self.complete_text(system=system, user=user, temperature=temperature)
        if not text:
            return None
        return parse_json_from_text(text)

    def _extract_message_text(self, msg: Dict[str, Any]) -> str:
        content = msg.get("content")
        if isinstance(content, str):
            text = content.strip()
            if text:
                return text
        elif isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    t = item.get("text")
                    if isinstance(t, str) and t.strip():
                        parts.append(t.strip())
            merged = "\n".join([x for x in parts if x.strip()]).strip()
            if merged:
                return merged
        for key in ("reasoning_content", "reasoning", "output_text", "text"):
            v = msg.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
            if isinstance(v, list):
                items = [str(x).strip() for x in v if str(x).strip()]
                if items:
                    return "\n".join(items)
        return ""


class TeacherRouter:
    def __init__(self, teachers: List[OpenAICompatTeacher]) -> None:
        self.teachers = [t for t in teachers if t is not None]

    def available(self) -> bool:
        return bool(self.teachers)

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.0,
        task: str = "",
    ) -> Optional[Dict[str, Any]]:
        if not self.teachers:
            return None
        for teacher in self.teachers:
            obj = teacher.complete_json(system=system, user=user, temperature=temperature)
            if isinstance(obj, dict):
                return obj
            if task:
                print(f"[autoskill-agent] {teacher.name} returned invalid JSON for {task}, trying fallback.")
            else:
                print(f"[autoskill-agent] {teacher.name} returned invalid JSON, trying fallback.")
        return None


class OpenAICompatEmbeddingClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_s: float = 90.0,
        name: str = "embedding",
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.api_key = str(api_key or "")
        self.model = str(model or "")
        self.timeout_s = float(timeout_s)
        self.name = str(name or "embedding")

    def available(self) -> bool:
        return bool(self.base_url and self.model)

    def embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        payload = {
            "model": self.model,
            "input": [str(x or "") for x in texts],
            "encoding_format": "float",
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        url = f"{self.base_url}/embeddings"
        req = urllib.request.Request(
            url=url,
            method="POST",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", errors="replace")
            except Exception:
                detail = str(e)
            print(f"[autoskill-agent] {self.name} embedding HTTP {e.code}: {detail}")
            return None
        except Exception as e:
            print(f"[autoskill-agent] {self.name} embedding request failed: {e}")
            return None

        try:
            obj = json.loads(raw)
        except Exception:
            print(f"[autoskill-agent] {self.name} embedding returned non-json body.")
            return None
        data = obj.get("data")
        if not isinstance(data, list):
            return None
        rows = []
        for item in data:
            if not isinstance(item, dict):
                continue
            emb = item.get("embedding")
            if not isinstance(emb, list):
                continue
            vec = []
            ok = True
            for x in emb:
                try:
                    vec.append(float(x))
                except Exception:
                    ok = False
                    break
            if ok and vec:
                rows.append((int(item.get("index") or len(rows)), vec))
        if not rows:
            return None
        rows.sort(key=lambda x: x[0])
        vectors = [x[1] for x in rows]
        if len(vectors) != len(texts):
            return None
        return vectors
