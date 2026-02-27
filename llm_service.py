import requests
import os
DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY')
#我在这里把api key设成了环境变量


# API Key


URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"


def call_llm(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }

    payload = {
        "model": "ep-20260227221235-8w4xg",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(URL, headers=headers, json=payload)

    result = response.json()

    # 防止接口报错时崩溃
    if "choices" not in result:
        return f"接口错误: {result}"

    return result["choices"][0]["message"]["content"]