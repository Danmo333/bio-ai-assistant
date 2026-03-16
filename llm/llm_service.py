from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import requests

from config import DOUBAO_API_KEY, LLM_URL, MODEL_ID


def _clear_proxy_env() -> None:
    # 彻底清除系统代理，避免 requests 走代理导致超时/失败
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)


def call_llm(messages: List[Dict[str, Any]]) -> str:
    """
    调用豆包（火山方舟）Chat Completions 接口。
    为稳定起见先使用非流式（stream=False），避免你当前前端/后端尚未接 SSE 时的复杂度。
    """
    _clear_proxy_env()

    if not DOUBAO_API_KEY:
        return "模型调用失败：未配置 DOUBAO_API_KEY"

    start = time.time()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
    }

    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 300,
        "stream": False,
    }

    try:
        response = requests.post(
            LLM_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        return f"模型调用失败：{e}"

    end = time.time()
    print("LLM响应时间:", end - start)

    choices = result.get("choices")
    if not choices:
        return "模型调用失败：无返回 choices"

    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        return "模型调用失败：无返回 content"

    return str(content)

