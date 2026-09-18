from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

from agents.coordinator import classify_query
from agents.hr_agent import ask_hr_agent
from agents.policy_agent import ask_policy_agent
from agents.leave_agent import ask_leave_agent

load_dotenv()

app = Flask(__name__)

SUPPORTED = {"POLICY", "LEAVE", "GENERAL"}

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
        category = classify_query(question)

        # Never route unsupported questions to the HR agent.
        if category not in SUPPORTED:
            return jsonify({
                "success": False,
                "category": "IRRELEVANT",
                "message": "I can help only with supported HR services such as company policies, leave, employee information, onboarding, and general HR support."
            })

        if category == "POLICY":
            answer = ask_policy_agent(question)
            agent = "Policy Agent"
        elif category == "LEAVE":
            answer = ask_leave_agent(question)
            agent = "Leave Agent"
        else:
            answer = ask_hr_agent(question)
            agent = "HR Assistant"

        return jsonify({
            "success": True,
            "category": category,
            "agent": agent,
            "message": str(answer).strip()
        })

    except Exception as e:
        print("ERROR:", repr(e))
        return jsonify({
            "success": False,
            "message": f"ERROR: {str(e)}"
        }), 503

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
