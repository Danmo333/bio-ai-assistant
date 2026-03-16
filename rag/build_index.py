from __future__ import annotations

import os
import re
import pickle
from pathlib import Path
from typing import Dict, List, Any

from utils.text_splitter import split_text
from .embedding import build_embeddings
from docx import Document

BASE_DIR = Path(__file__).resolve().parent.parent

# 你在项目根目录下的生物知识库目录结构：
# biology/
#   mandatory_1/
#       chapter1.txt
#       chapter2.txt
#   mandatory_2/
#       ...
BIOLOGY_DIR = BASE_DIR / "biology"

# 向量索引保存位置
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"
VECTOR_STORE_PATH = VECTOR_STORE_DIR / "biology_index.pkl"


def load_all_chapter_texts() -> List[str]:
    """
    加载 biology/ 目录下所有 .txt 文件的内容，每个文件一个整体文本。
    例如 biology/mandatory_1/chapter1.txt 等。
    """
    if not BIOLOGY_DIR.exists():
        raise FileNotFoundError(f"找不到生物知识库目录: {BIOLOGY_DIR}")

    texts = []
    # 定义正则表达式：匹配 ![img](任意内容) 格式的图片标签
    # 正则说明：!\[img\] 匹配 "![img]"，\(.*?\) 非贪婪匹配括号内的任意内容
    img_pattern = re.compile(r'!\[img\]\(.*?\)')

    for path in sorted(BIOLOGY_DIR.rglob("*.docx")):
        try:
            doc = Document(path)

            # 拼接所有段落文本
            raw_content = "\n".join(p.text for p in doc.paragraphs).strip()
            # 核心修改：过滤图片标签
            cleaned_content = img_pattern.sub('', raw_content)
            # 再次去除首尾空白，确保过滤后无空文本
            cleaned_content = cleaned_content.strip()

            # 仅添加非空的清洗后内容
            if cleaned_content:
                texts.append(cleaned_content)
                print(f"✅ 处理完成: {path.name}，清洗后文本长度: {len(cleaned_content)}")
            else:
                print(f"⚠️ 警告: {path.name} 清洗后无有效文本，已跳过")

        except Exception as e:
            print(f"❌ 处理文件失败 {path}: {str(e)}")
            continue
    return texts

def build_index() -> None:
    """
    构建 RAG 所需的向量索引：
    1. 遍历 biology/ 下所有 .txt 文件（如 mandatory_1/chapter1.txt 等）
    2. 每个文件按滑动窗口切分成 500~1000 字的片段
    3. 使用 TF‑IDF 生成 embedding
    4. 将（chunks, vectorizer, matrix）持久化到磁盘
    """
    print(f"扫描知识库目录: {BIOLOGY_DIR}")
    texts = load_all_chapter_texts()

    all_chunks: List[str] = []
    for text in texts:
        file_chunks = split_text(text, chunk_size=300, overlap=50)
        all_chunks.extend(file_chunks)

    print(f"共生成分片: {len(all_chunks)}")

    if not all_chunks:
        raise ValueError("知识库内容为空，无法构建索引。")

    print("计算 Embedding 向量...")
    embeddings = build_embeddings(all_chunks)

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "chunks": all_chunks,
        "embeddings": embeddings,
    }

    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(payload, f)

    print(f"向量索引已保存到: {VECTOR_STORE_PATH}")


if __name__ == "__main__":
    build_index()

