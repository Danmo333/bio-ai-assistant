from __future__ import annotations

from typing import List

import os
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_PATH


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        # 强制离线，禁止任何联网（避免 huggingface.co HEAD 请求）
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(EMBEDDING_MODEL_PATH))

        local_path = EMBEDDING_MODEL_PATH
        if os.path.exists(local_path):
            _MODEL = SentenceTransformer(
                local_path,
                local_files_only=True,
                trust_remote_code=True,
            )
        else:
            # 如果本地路径不存在，就不要尝试联网；直接报错引导用户配置
            raise FileNotFoundError(
                f"本地 embedding 模型路径不存在：{local_path}\n"
                f"请将模型放到该目录，或设置环境变量 EMBEDDING_MODEL_PATH。"
            )
    return _MODEL


def build_embeddings(chunks: List[str]) -> np.ndarray:
    """
    使用 SentenceTransformer 生成密集 embedding 向量，并进行归一化，方便用点积近似余弦相似度。
    返回形状为 (n_chunks, dim) 的 numpy 数组。
    """
    model = _get_model()
    embeddings = model.encode(
        chunks,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,  # 分批计算，避免内存溢出
    )
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """
    将查询问题转换为 embedding 向量，形状为 (1, dim)。
    """
    model = _get_model()
    emb = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return emb

