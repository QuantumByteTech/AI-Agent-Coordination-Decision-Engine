from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import traceback

from agents.coordinator import ask_coordinator
from auth import authenticate_employee

load_dotenv()

app = Flask(__name__)

# Secret key required for login sessions
app.secret_key = "worksphere-dev-secret-2026"


# =========================================================
# MAIN DASHBOARD
# =========================================================

@app.route("/")
def index():

    # User must be logged in
    if "employee_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        employee_name=session["employee_name"],
        employee_id=session["employee_id"]
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # -------------------------
    # SHOW LOGIN PAGE
    # -------------------------
    if request.method == "GET":

        # Already logged in
        if "employee_id" in session:
            return redirect(url_for("index"))

        return render_template("login.html")


    # -------------------------
    # PROCESS LOGIN
    # -------------------------

    employee_id = request.form.get("employee_id", "").strip()
    password = request.form.get("password", "")

    # Validate Employee ID
    if not employee_id.isdigit():

        return render_template(
            "login.html",
            error="Please enter a valid Employee ID."
        )


    # Authenticate employee
    employee = authenticate_employee(
        int(employee_id),
        password
    )


    # Invalid credentials
    if not employee:

        return render_template(
            "login.html",
            error="Invalid Employee ID or password."
        )


    # -------------------------
    # CREATE SESSION
    # -------------------------

    session.clear()

    session["employee_id"] = employee["employee_id"]
    session["employee_name"] = employee["name"]


    # -------------------------
    # GO TO DASHBOARD
    # -------------------------

    return redirect(url_for("index"))


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    # Completely remove login session
    session.clear()

    # Go back to login page
    return redirect(url_for("login"))


# =========================================================
# CHAT API
# =========================================================

@app.post("/api/chat")
def chat():

    # Only logged-in employees can use the assistant
    if "employee_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please sign in first."
        }), 401


    # Get request data
    data = request.get_json(silent=True) or {}

    question = (data.get("question") or "").strip()


    # Empty question
    if not question:

        return jsonify({
            "success": False,
            "message": "Please enter an HR-related question."
        }), 400


    # IMPORTANT:
    # Employee ID comes from the authenticated session.
    # The user cannot choose another employee here.
    employee_id = session["employee_id"]


    try:

        result = ask_coordinator(
            question,
            employee_id=employee_id
        )

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


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )