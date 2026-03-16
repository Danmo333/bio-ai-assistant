SYSTEM_PROMPT = """
你是一名专业的高中生物学科助教。

回答规则：
1. 简明讲解
2. 如果是题目，给出解题思路
3. 表达清晰，适合高中生理解
"""


def build_messages(question, history, context: str = ""):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": f"""
    参考知识：

    {context}

    学生问题：
    {question}
    """
    })

    return messages