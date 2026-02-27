SYSTEM_PROMPT = """
你是一名专业的高中生物学科助教。

回答规则：
1. 分步骤讲解
2. 指出对应知识点
3. 如果是题目，给出解题思路
4. 表达清晰，适合高中生理解
"""

def build_prompt(question, history=""):
    return f"""
{SYSTEM_PROMPT}

历史对话：
{history}

学生问题：
{question}
"""