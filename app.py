import os
import time
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from prompt import build_messages
from llm.llm_service import call_llm
from database.chat_service import save_chat
from database.db import init_db
from database.analysis import get_chat_stats, get_top_questions
from database.user_service import create_user, verify_user
from rag.retriever import retrieve_context

app = Flask(__name__)
# 为了满足“每次重启都要重新登录”的需求，这里每次启动都生成新的 secret_key，
# 这样旧的浏览器会话 Cookie 会自动失效，打开后一定会先看到登录/注册页面。
app.secret_key = os.urandom(24)

init_db()


def login_required(role: str | None = None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")
            user_role = session.get("role")
            if not user_id:
                return redirect(url_for("login"))
            if role and user_role != role:
                return "无权限访问该页面", 403
            return f(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/")
def root():
    # 未登录统一跳到登录页
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 根据角色跳转
    role = session.get("role")
    if role == "teacher":
        return redirect(url_for("teacher"))
    return redirect(url_for("student"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    user = verify_user(username, password)
    if not user:
        return render_template("login.html", error="用户名或密码错误")

    user_id, uname, role = user
    session["user_id"] = user_id
    session["username"] = uname
    session["role"] = role

    if role == "teacher":
        return redirect(url_for("teacher"))
    return redirect(url_for("student"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("login.html", mode="register")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    role = request.form.get("role") or "student"

    if not username or not password:
        return render_template("login.html", mode="register", error="用户名和密码不能为空")

    ok = create_user(username, password, role)
    if not ok:
        return render_template("login.html", mode="register", error="用户名已存在或角色不合法")

    return render_template("login.html", success="注册成功，请登录")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/student")
@login_required(role="student")
def student():
    username = session.get("username")
    return render_template("index.html", username=username)


@app.route("/chat", methods=["POST"])
@login_required(role="student")
def chat():
    t0 = time.perf_counter()
    data = request.get_json(silent=True) or {}

    # 兼容两种前端请求格式：
    # 1) {question: "..."}
    # 2) {messages: [{role, content}, ...]}
    question = (data.get("question") or "").strip()
    history = data.get("messages") or []

    if not question and isinstance(history, list) and history:
        last = history[-1] or {}
        if isinstance(last, dict) and last.get("role") == "user":
            question = (last.get("content") or "").strip()

    # 清洗 history：只保留 role/content
    cleaned_history = []
    if isinstance(history, list):
        for m in history:
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                cleaned_history.append({"role": role, "content": content})

    if not question:
        return jsonify({"answer": "请先输入问题。"}), 400

    # 使用 RAG：先从知识库检索相关分片
    t_rag_start = time.perf_counter()
    context, found = retrieve_context(question, top_k=3)
    t_rag_end = time.perf_counter()

    if not found:
        # 没有检索到足够相关的内容，按照你的需求直接提示“未找到答案”
        return jsonify({"answer": "当前知识库中未找到与你问题高度相关的内容，请换个问法或联系老师。"})

    messages = build_messages(question, cleaned_history, context=context)
    t_llm_start = time.perf_counter()
    answer = call_llm(messages)
    t_llm_end = time.perf_counter()

    save_chat(question, answer)
    t1 = time.perf_counter()

    print(
        "耗时统计: "
        f"RAG={t_rag_end - t_rag_start:.3f}s, "
        f"LLM={t_llm_end - t_llm_start:.3f}s, "
        f"TOTAL={t1 - t0:.3f}s"
    )
    return jsonify({"answer": answer})

@app.route("/teacher", methods=["GET"])
@login_required(role="teacher")
def teacher():
    stats = get_chat_stats()
    top_questions = get_top_questions(limit=20)
    return render_template("teacher.html", stats=stats, top_questions=top_questions)


if __name__ == "__main__":
    app.run(debug=True)