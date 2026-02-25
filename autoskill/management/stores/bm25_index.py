"""
Persistent BM25 inverted index for local skill retrieval.

Storage layout (under one directory):
- <name>.meta.json
- <name>.postings.json
- <name>.doc_len.json
- <name>.doc_tf.json
- <name>.doc_hash.json
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import threading
from collections import Counter
from typing import Dict, Iterable, List, Optional

from .hybrid_rank import tokenize_for_bm25


class PersistentBM25Index:
    def __init__(self, *, dir_path: str, name: str = "skills-bm25") -> None:
        self._dir = os.path.abspath(os.path.expanduser(str(dir_path)))
        self._name = str(name or "skills-bm25").strip() or "skills-bm25"
        self._meta_path = os.path.join(self._dir, f"{self._name}.meta.json")
        self._postings_path = os.path.join(self._dir, f"{self._name}.postings.json")
        self._doc_len_path = os.path.join(self._dir, f"{self._name}.doc_len.json")
        self._doc_tf_path = os.path.join(self._dir, f"{self._name}.doc_tf.json")
        self._doc_hash_path = os.path.join(self._dir, f"{self._name}.doc_hash.json")

        self._lock = threading.RLock()
        self._postings: Dict[str, Dict[str, int]] = {}
        self._doc_len: Dict[str, int] = {}
        self._doc_tf: Dict[str, Dict[str, int]] = {}
        self._doc_hash: Dict[str, str] = {}
        self._doc_count = 0
        self._total_terms = 0

        os.makedirs(self._dir, exist_ok=True)
        self.load()

    @property
    def storage_paths(self) -> Dict[str, str]:
        """Returns absolute paths for persisted index files."""

        return {
            "meta": self._meta_path,
            "postings": self._postings_path,
            "doc_len": self._doc_len_path,
            "doc_tf": self._doc_tf_path,
            "doc_hash": self._doc_hash_path,
        }

    def ids(self) -> List[str]:
        with self._lock:
            return list(self._doc_len.keys())

    def has(self, doc_id: str) -> bool:
        sid = str(doc_id or "").strip()
        if not sid:
            return False
        with self._lock:
            return sid in self._doc_len

    def doc_hash_of(self, doc_id: str) -> str:
        sid = str(doc_id or "").strip()
        if not sid:
            return ""
        with self._lock:
            return str(self._doc_hash.get(sid) or "")

    def upsert(self, doc_id: str, text: str) -> bool:
        sid = str(doc_id or "").strip()
        if not sid:
            return False
        body = str(text or "")
        h = _hash_text(body)

        with self._lock:
            old_hash = self._doc_hash.get(sid)
            if old_hash and old_hash == h and sid in self._doc_len:
                return False

            old_tf = self._doc_tf.get(sid, {})
            old_len = int(self._doc_len.get(sid, 0))
            if old_tf:
                self._remove_doc_terms_locked(sid=sid, tf=old_tf)
                self._total_terms = max(0, int(self._total_terms) - max(0, old_len))
            else:
                self._doc_count += 1

            toks = tokenize_for_bm25(body)
            tf = Counter(toks)
            tf_dict = {str(k): int(v) for k, v in tf.items() if str(k) and int(v) > 0}
            dlen = int(sum(tf_dict.values()))

            self._doc_tf[sid] = tf_dict
            self._doc_len[sid] = dlen
            self._doc_hash[sid] = h
            self._total_terms += dlen
            self._add_doc_terms_locked(sid=sid, tf=tf_dict)
            return True

    def delete(self, doc_id: str) -> bool:
        sid = str(doc_id or "").strip()
        if not sid:
            return False
        with self._lock:
            tf = self._doc_tf.pop(sid, None)
            if tf is None:
                return False
            dlen = int(self._doc_len.pop(sid, 0))
            self._doc_hash.pop(sid, None)
            self._remove_doc_terms_locked(sid=sid, tf=tf)
            self._doc_count = max(0, int(self._doc_count) - 1)
            self._total_terms = max(0, int(self._total_terms) - max(0, dlen))
            return True

    def search_scores(
        self,
        query: str,
        *,
        keys: Optional[Iterable[str]] = None,
        top_k: int = 0,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> Dict[str, float]:
        q_terms = tokenize_for_bm25(query)
        if not q_terms:
            return {}

        with self._lock:
            n_docs = int(self._doc_count)
            if n_docs <= 0:
                return {}
            avgdl = (float(self._total_terms) / float(n_docs)) if n_docs > 0 else 1.0
            if avgdl <= 0:
                avgdl = 1.0

            allowed: Optional[set[str]] = None
            if keys is not None:
                allowed = {str(k).strip() for k in keys if str(k).strip()}
                if not allowed:
                    return {}

            q_tf = Counter(q_terms)
            raw: Dict[str, float] = {}
            for term, qf in q_tf.items():
                postings = self._postings.get(term)
                if not postings:
                    continue
                n_qi = int(len(postings))
                idf = math.log(1.0 + ((n_docs - n_qi + 0.5) / (n_qi + 0.5)))
                for sid, f in postings.items():
                    if allowed is not None and sid not in allowed:
                        continue
                    dl = max(1, int(self._doc_len.get(sid, 0)))
                    ff = int(f)
                    if ff <= 0:
                        continue
                    denom = ff + float(k1) * (1.0 - float(b) + float(b) * (dl / avgdl))
                    if denom <= 0:
                        continue
                    raw[sid] = float(raw.get(sid, 0.0)) + float(qf) * idf * (
                        (ff * (float(k1) + 1.0)) / denom
                    )

        if not raw:
            return {}
        max_score = max(raw.values())
        if max_score <= 0:
            return {}
        norm = {sid: max(0.0, float(sc) / float(max_score)) for sid, sc in raw.items()}
        k = int(top_k or 0)
        if k > 0 and len(norm) > k:
            ordered = sorted(norm.items(), key=lambda x: x[1], reverse=True)[:k]
            return {sid: float(sc) for sid, sc in ordered}
        return norm

    def load(self) -> None:
        with self._lock:
            self._reset_locked()

            if not os.path.isfile(self._meta_path):
                return
            try:
                meta = _read_json(self._meta_path)
                self._postings = _as_postings(_read_json(self._postings_path))
                self._doc_len = _as_doc_len(_read_json(self._doc_len_path))
                self._doc_tf = _as_doc_tf(_read_json(self._doc_tf_path))
                self._doc_hash = _as_doc_hash(_read_json(self._doc_hash_path))
                self._doc_count = int(meta.get("doc_count") or len(self._doc_len))
                self._total_terms = int(meta.get("total_terms") or sum(self._doc_len.values()))
            except Exception:
                self._postings = {}
                self._doc_len = {}
                self._doc_tf = {}
                self._doc_hash = {}
                self._doc_count = 0
                self._total_terms = 0
                return

            self._doc_count = max(0, int(self._doc_count))
            if self._doc_count <= 0:
                self._doc_count = int(len(self._doc_len))
            self._total_terms = max(0, int(self._total_terms))
            if self._total_terms <= 0 and self._doc_len:
                self._total_terms = int(sum(self._doc_len.values()))

    def validate(self, *, strict: bool = True) -> Dict[str, object]:
        """
        Validates in-memory BM25 structures and on-disk file presence.

        Returns:
        - ok: bool
        - issues: list[str]
        - counters: dict[str, int]
        """

        with self._lock:
            issues: List[str] = []
            paths = self.storage_paths
            files_exist = {k: os.path.isfile(p) for k, p in paths.items()}
            have_any = any(files_exist.values())
            have_all = all(files_exist.values())
            if have_any and not have_all:
                missing = [k for k, ok in files_exist.items() if not ok]
                issues.append(f"incomplete_files:{','.join(missing)}")

            doc_len_ids = set(self._doc_len.keys())
            doc_tf_ids = set(self._doc_tf.keys())
            doc_hash_ids = set(self._doc_hash.keys())

            if doc_len_ids != doc_tf_ids:
                issues.append("doc_len_doc_tf_id_mismatch")
            if doc_hash_ids and doc_hash_ids != doc_len_ids:
                issues.append("doc_hash_id_mismatch")

            expected_doc_count = int(len(doc_len_ids))
            if int(self._doc_count) != expected_doc_count:
                issues.append("doc_count_mismatch")

            total_terms = int(sum(max(0, int(v)) for v in self._doc_len.values()))
            if int(self._total_terms) != total_terms:
                issues.append("total_terms_mismatch")

            bad_len = 0
            for sid, tf in self._doc_tf.items():
                want_len = int(self._doc_len.get(sid, -1))
                got_len = int(sum(int(v) for v in tf.values()))
                if want_len != got_len:
                    bad_len += 1
            if bad_len > 0:
                issues.append(f"doc_len_tf_sum_mismatch:{bad_len}")

            if strict:
                bad_postings = 0
                for term, posting in self._postings.items():
                    t = str(term or "").strip()
                    if not t:
                        bad_postings += 1
                        continue
                    for sid, freq in posting.items():
                        if sid not in doc_len_ids:
                            bad_postings += 1
                            continue
                        tf = self._doc_tf.get(sid, {})
                        if int(tf.get(t, 0)) != int(freq):
                            bad_postings += 1
                if bad_postings > 0:
                    issues.append(f"postings_tf_mismatch:{bad_postings}")

            ok = len(issues) == 0
            return {
                "ok": ok,
                "issues": issues,
                "counters": {
                    "doc_count": int(self._doc_count),
                    "doc_len_count": int(len(self._doc_len)),
                    "doc_tf_count": int(len(self._doc_tf)),
                    "doc_hash_count": int(len(self._doc_hash)),
                    "postings_terms": int(len(self._postings)),
                    "total_terms": int(self._total_terms),
                },
                "files": files_exist,
            }

    def rebuild_from_docs(self, docs: Dict[str, str]) -> Dict[str, int]:
        """Resets index and rebuilds postings/statistics from given docs."""

        with self._lock:
            self._reset_locked()
            built = 0
            for sid, txt in dict(docs or {}).items():
                if self.upsert(str(sid), str(txt or "")):
                    built += 1
            self.save()
            return {"built": int(built), "docs": int(len(docs or {}))}

    def save(self) -> None:
        with self._lock:
            meta = {
                "version": 1,
                "doc_count": int(self._doc_count),
                "total_terms": int(self._total_terms),
                "name": self._name,
            }
            _write_json_atomic(self._meta_path, meta)
            _write_json_atomic(self._postings_path, self._postings)
            _write_json_atomic(self._doc_len_path, self._doc_len)
            _write_json_atomic(self._doc_tf_path, self._doc_tf)
            _write_json_atomic(self._doc_hash_path, self._doc_hash)

    def _add_doc_terms_locked(self, *, sid: str, tf: Dict[str, int]) -> None:
        for term, freq in (tf or {}).items():
            t = str(term or "").strip()
            f = int(freq or 0)
            if not t or f <= 0:
                continue
            posting = self._postings.setdefault(t, {})
            posting[sid] = f

    def _remove_doc_terms_locked(self, *, sid: str, tf: Dict[str, int]) -> None:
        for term in list((tf or {}).keys()):
            t = str(term or "").strip()
            if not t:
                continue
            posting = self._postings.get(t)
            if not posting:
                continue
            posting.pop(sid, None)
            if not posting:
                self._postings.pop(t, None)

    def _reset_locked(self) -> None:
        self._postings = {}
        self._doc_len = {}
        self._doc_tf = {}
        self._doc_hash = {}
        self._doc_count = 0
        self._total_terms = 0


def _hash_text(text: str) -> str:
    return hashlib.sha1(str(text or "").encode("utf-8")).hexdigest()


def _read_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return dict(obj) if isinstance(obj, dict) else {}


def _write_json_atomic(path: str, obj: Dict) -> None:
    p = str(path)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, p)


def _as_postings(obj: Dict) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for term, posting in dict(obj or {}).items():
        t = str(term or "").strip()
        if not t or not isinstance(posting, dict):
            continue
        p2: Dict[str, int] = {}
        for sid, freq in posting.items():
            s = str(sid or "").strip()
            if not s:
                continue
            try:
                f = int(freq)
            except Exception:
                continue
            if f > 0:
                p2[s] = f
        if p2:
            out[t] = p2
    return out


def _as_doc_len(obj: Dict) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for sid, val in dict(obj or {}).items():
        s = str(sid or "").strip()
        if not s:
            continue
        try:
            n = int(val)
        except Exception:
            continue
        out[s] = max(0, n)
    return out


def _as_doc_tf(obj: Dict) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for sid, tf in dict(obj or {}).items():
        s = str(sid or "").strip()
        if not s or not isinstance(tf, dict):
            continue
        tf2: Dict[str, int] = {}
        for term, freq in tf.items():
            t = str(term or "").strip()
            if not t:
                continue
            try:
                f = int(freq)
            except Exception:
                continue
            if f > 0:
                tf2[t] = f
        out[s] = tf2
    return out


def _as_doc_hash(obj: Dict) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for sid, h in dict(obj or {}).items():
        s = str(sid or "").strip()
        hh = str(h or "").strip()
        if s and hh:
            out[s] = hh
    return out
