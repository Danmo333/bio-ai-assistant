import os

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")

LLM_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

MODEL_ID = "ep-20260227221235-8w4xg"

DATABASE_PATH = "database/chat.db"

# Embedding 模型本地路径（优先使用环境变量 EMBEDDING_MODEL_PATH）
EMBEDDING_MODEL_PATH = os.getenv(
    "EMBEDDING_MODEL_PATH",
    r"D:\model\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2",
)