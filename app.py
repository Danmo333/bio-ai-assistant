from flask import Flask, render_template, request, jsonify
from llm_service import call_llm
from prompt import build_prompt

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question")
    history = data.get("history", "")

    prompt = build_prompt(question, history)
    answer = call_llm(prompt)

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)