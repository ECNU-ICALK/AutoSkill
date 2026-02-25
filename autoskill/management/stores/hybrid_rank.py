"""
Hybrid retrieval helpers for skill search.

This module provides:
- lightweight BM25 keyword scoring (dependency-free)
- score blending for vector + BM25 hybrid retrieval
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, List


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]|[^\W\d_]", re.UNICODE)
_STOPWORDS = {
    "the",
    "and",
    "or",
    "to",
    "a",
    "an",
    "of",
    "in",
    "on",
    "for",
    "with",
    "is",
    "are",
    "be",
    "by",
    "from",
    "at",
    "as",
    "this",
    "that",
    "it",
    "i",
    "you",
    "we",
}


def _tokenize(text: str) -> List[str]:
    tokens = [t.lower().strip() for t in _TOKEN_RE.findall(text or "")]
    out: List[str] = []
    for t in tokens:
        if not t:
            continue
        if t in _STOPWORDS:
            continue
        out.append(t)
    return out


def tokenize_for_bm25(text: str) -> List[str]:
    """Public tokenizer used by BM25 helpers and persistent index."""

    return _tokenize(text)


def bm25_normalized_scores(
    query: str,
    docs: Dict[str, str],
    *,
    k1: float = 1.5,
    b: float = 0.75,
) -> Dict[str, float]:
    """
    Computes BM25 scores and normalizes them to [0, 1] by the max score in this set.

    Args:
        query: user query text
        docs: mapping of doc_id -> doc_text
    """

    if not docs:
        return {}

    q_terms = tokenize_for_bm25(query)
    if not q_terms:
        return {str(doc_id): 0.0 for doc_id in docs.keys()}

    q_tf = Counter(q_terms)
    doc_tf: Dict[str, Counter] = {}
    doc_len: Dict[str, int] = {}
    df = Counter()

    for doc_id, text in docs.items():
        did = str(doc_id)
        toks = tokenize_for_bm25(text)
        tf = Counter(toks)
        doc_tf[did] = tf
        doc_len[did] = len(toks)
        for term in tf.keys():
            df[term] += 1

    n_docs = max(1, len(doc_tf))
    avgdl = (sum(doc_len.values()) / float(n_docs)) if n_docs > 0 else 1.0
    if avgdl <= 0:
        avgdl = 1.0

    raw: Dict[str, float] = {}
    for did, tf in doc_tf.items():
        dl = max(1, int(doc_len.get(did, 0)))
        score = 0.0
        for term, qf in q_tf.items():
            f = int(tf.get(term, 0))
            if f <= 0:
                continue
            n_qi = int(df.get(term, 0))
            idf = math.log(1.0 + ((n_docs - n_qi + 0.5) / (n_qi + 0.5)))
            denom = f + float(k1) * (1.0 - float(b) + float(b) * (dl / avgdl))
            if denom <= 0:
                continue
            score += float(qf) * idf * ((f * (float(k1) + 1.0)) / denom)
        raw[did] = float(score)

    max_score = max(raw.values()) if raw else 0.0
    if max_score <= 0:
        return {did: 0.0 for did in doc_tf.keys()}

    return {did: max(0.0, float(sc) / float(max_score)) for did, sc in raw.items()}


def blend_scores(
    *,
    vector_scores: Dict[str, float],
    bm25_scores: Dict[str, float],
    bm25_weight: float,
    use_vector: bool,
) -> Dict[str, float]:
    """
    Blends vector and BM25 scores by weighted sum.

    final_score = (1 - bm25_weight) * vector_score + bm25_weight * bm25_score
    """

    w = float(bm25_weight)
    if w < 0.0:
        w = 0.0
    if w > 1.0:
        w = 1.0

    if not use_vector or not vector_scores:
        return {str(k): float(v) for k, v in (bm25_scores or {}).items()}
    if w <= 0.0:
        return {str(k): float(v) for k, v in (vector_scores or {}).items()}
    if w >= 1.0:
        return {str(k): float(v) for k, v in (bm25_scores or {}).items()}

    out: Dict[str, float] = {}
    keys = set(_iter_keys(vector_scores)) | set(_iter_keys(bm25_scores))
    for k in keys:
        vs = float(vector_scores.get(k, 0.0))
        bs = float(bm25_scores.get(k, 0.0))
        out[k] = (1.0 - w) * vs + w * bs
    return out


def _iter_keys(d: Dict[str, float]) -> Iterable[str]:
    for k in (d or {}).keys():
        yield str(k)
