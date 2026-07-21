import atexit

from flask import Flask, request, jsonify, send_from_directory
from config import Config
from prompts import SYSTEM_PROMPT
from chat import retrieve_context, load_model_and_client

app = Flask(__name__, static_folder="static", static_url_path="")

model, client = load_model_and_client()
atexit.register(model.unload)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_query = data.get("message", "").strip()
    if not user_query:
        return jsonify({"error": "message is required"}), 400

    context = retrieve_context(user_query, Config.TOP_K)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"},
    ]

    try:
        answer = "".join(
            chunk.choices[0].delta.content or ""
            for chunk in client.complete_streaming_chat(messages)
            if chunk.choices
        )
    except Exception as e:
        return jsonify({"error": f"Model generation error: {e}"}), 500

    return jsonify({"answer": answer})


if __name__ == "__main__":
    print("\n--- AI ASSISTANT READY (web UI) ---")
    app.run(host="127.0.0.1", port=5050, debug=False)
