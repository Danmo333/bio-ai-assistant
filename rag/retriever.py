from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from .embedding import embed_query

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = BASE_DIR / "data" / "vector_store" / "biology_index.pkl"

_INDEX_CACHE: Dict[str, Any] | None = None


def _load_index() -> Dict[str, Any] | None:
    global _INDEX_CACHE
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    if not VECTOR_STORE_PATH.exists():
        return None

    with open(VECTOR_STORE_PATH, "rb") as f:
        _INDEX_CACHE = pickle.load(f)
    return _INDEX_CACHE


def retrieve_context(
    query: str,
    top_k: int = 3,
    score_threshold: float = 0.2,
) -> Tuple[str, bool]:
    """
    从向量索引中检索与问题最相关的 Top‑k 分片。
    使用 SentenceTransformer 的 embedding，点积近似余弦相似度。
    返回：
    - context: 拼接后的上下文字符串
    - found: 是否检索到足够相关的内容
    """
    index = _load_index()
    if index is None:
        # 没有索引文件时，直接返回未找到
        return "", False

    chunks: List[str] = index["chunks"]
    embeddings: np.ndarray = index["embeddings"]

    if not chunks or embeddings.size == 0:
        return "", False

    q_vec = embed_query(query)  # (1, dim)
    q = q_vec[0]  # (dim,)

    # 由于向量已经归一化，点积即为余弦相似度
    sims = embeddings @ q  # (n_chunks,)

    # 取相似度最高的 top_k
    top_indices = np.argsort(sims)[::-1][:top_k]
    selected: List[Tuple[int, float]] = [
        (int(i), float(sims[i])) for i in top_indices if sims[i] >= score_threshold
    ]

    if not selected:
        return "", False

    selected_sorted = sorted(selected, key=lambda x: x[1], reverse=True)
    context_parts = []
    for idx, score in selected_sorted:
        part = chunks[idx].strip()
        if part:
            context_parts.append(f"[相关度 {score:.2f}] {part}")

    context = "\n\n".join(context_parts)
    return context, True

