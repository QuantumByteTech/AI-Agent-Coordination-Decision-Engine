from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import traceback

from agents.coordinator import ask_coordinator

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({
            "success": False,
            "message": "Please enter an HR-related question."
        }), 400

    try:
        result = ask_coordinator(question)
        return jsonify(result)

    except Exception as e:
        print("\n========== CHAT ERROR ==========")
        traceback.print_exc()
        print("================================\n")

        return jsonify({
            "success": False,
            "category": "ERROR",
            "agent": "System",
            "message": str(e)
        }), 503


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
