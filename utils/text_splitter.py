from __future__ import annotations

from typing import List


def split_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 200,
) -> List[str]:
    """
    将长文本按滑动窗口切分为多个片段（适合中文 500~1000 字的粒度）。

    - chunk_size: 每个分片的最大长度（字符数）
    - overlap: 相邻分片的重叠长度，保证语义连续性
    """
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        # 下一段从 chunk_size - overlap 开始，实现滑动窗口
        start += max(chunk_size - overlap, 1)

    return chunks

