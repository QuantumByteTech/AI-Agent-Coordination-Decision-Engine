from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.department_api import router as department_router
from app.api.employee_api import router as employee_router
from app.api.leave_api import router as leave_router
from app.api.attendance_api import router as attendance_router
from app.api.lifecycle_api import router as lifecycle_router
from app.api.workflow_api import router as workflow_router
from app.api.agent_api import router as agent_router
from app.api.auth_api import router as auth_router

from app.database.database import get_db
from app.database.models import User
from app.auth.dependencies import get_current_user, require_hr
from app.services.workflow_service import workflow_service
from app.services.dashboard_service import dashboard_service
from app.agents.policy_agent import policy_agent
from app.agents.employee_agent import EmployeeAgent
from app.agents.leave_agent import LeaveAgent
from app.agents.attendance_agent import AttendanceAgent


app = FastAPI(
    title="AI Agent Coordination & Decision Engine",
    description=(
        "Enterprise HR workflow automation, "
        "multi-agent coordination and decision support platform."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(attendance_router)
app.include_router(lifecycle_router)
app.include_router(workflow_router)
app.include_router(agent_router)
app.include_router(auth_router)
app.include_router(department_router)


class HRRequest(BaseModel):
    employee_id: int
    request: str


# These agents perform read-only lookups; they do not change HR records.
employee_agent = EmployeeAgent()
leave_agent = LeaveAgent()
attendance_agent = AttendanceAgent()


@app.get("/")
def root():
    return {
        "success": True,
        "system": "AI Agent Coordination & Decision Engine",
        "status": "online",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}



def _response(message: str, agent_result: dict, task: str):
    """Build an honest response with evidence from actual read-only results."""
    agent_name = agent_result.get("agent", task)
    successful = agent_result.get("success") is True

    evidence = []
    finding = ""

    if not successful:
        finding = agent_result.get(
            "message", "The agent could not complete the lookup."
        )

    elif isinstance(agent_result.get("employee"), dict):
        employee = agent_result["employee"]
        name = " ".join(
            str(employee.get(key, "")).strip()
            for key in ("first_name", "last_name")
            if employee.get(key)
        )
        finding = (
            f"Retrieved employee profile for {name or 'employee'}. "
            f"Employee code: {employee.get('employee_code', 'unavailable')}; "
            f"status: {employee.get('employment_status', 'unavailable')}."
        )
        evidence.append({
            "id": 1,
            "source": agent_name,
            "finding": finding,
            "details": {"employee": employee},
        })

    elif isinstance(agent_result.get("policies"), list):
        policies = agent_result["policies"]
        count = len(policies)

        if count:
            for index, policy in enumerate(policies, start=1):
                if not isinstance(policy, dict):
                    continue

                policy_name = policy.get("policy_name", "Unnamed policy")
                description = policy.get("description", "")
                finding = (
                    f"{policy_name}: {description}"
                    if description else policy_name
                )
                evidence.append({
                    "id": index,
                    "source": agent_name,
                    "finding": finding,
                    "details": {"policy": policy},
                })

            finding = f"Retrieved {len(evidence)} HR policy record(s)."
        else:
            finding = agent_result.get(
                "message",
                "No matching HR policies were found in the database."
            )

    elif isinstance(agent_result.get("leave_balance"), dict):
        balance = agent_result["leave_balance"]
        finding = (
            "Leave balance retrieved: "
            f"casual={balance.get('casual_leave', 'unavailable')}, "
            f"sick={balance.get('sick_leave', 'unavailable')}, "
            f"earned={balance.get('earned_leave', 'unavailable')}."
        )
        evidence.append({
            "id": 1,
            "source": agent_name,
            "finding": finding,
            "details": {"leave_balance": balance},
        })

    elif isinstance(agent_result.get("summary"), dict):
        summary = agent_result["summary"]
        finding = (
            "Attendance summary retrieved: "
            f"{summary.get('attendance_percentage', 'unavailable')}% attendance."
        )
        evidence.append({
            "id": 1,
            "source": agent_name,
            "finding": finding,
            "details": {"summary": summary},
        })

    elif isinstance(agent_result.get("leave_history"), list):
        history = agent_result["leave_history"]
        finding = f"Retrieved {len(history)} leave history record(s)."
        if history:
            evidence.append({
                "id": 1,
                "source": agent_name,
                "finding": finding,
                "details": {"leave_history": history},
            })

    elif successful:
        finding = agent_result.get(
            "message", "The lookup completed, but no recognized result was returned."
        )

    has_evidence = bool(evidence)
    completed = successful and (
        has_evidence or (
            isinstance(agent_result.get("policies"), list)
            and len(agent_result["policies"]) == 0
        )
    )

    if not successful:
        user_message = finding
        status = "unable_to_complete"
    elif not has_evidence:
        user_message = finding
        status = "no_results"
    else:
        user_message = message
        status = "completed"

    return {
        "success": successful,
        "mode": "read_only_self_service",
        "message": user_message,
        "plan": [{
            "step": 1,
            "agent": agent_name,
            "task": task,
            "status": status,
            "finding": finding,
        }],
        "results": [agent_result],
        "decision": {
            "decision": (
                "EVIDENCE_RETRIEVED" if has_evidence
                else "NO_RESULTS" if successful
                else "LOOKUP_FAILED"
            ),
            "status": status,
            "recommendation": finding,
            "reasoning": (
                "The response is based on the read-only agent result."
                if has_evidence
                else "No usable evidence was returned by the agent."
            ),
            "evidence_count": len(evidence),
            "evidence": evidence,
            "missing_information": (
                [] if has_evidence
                else ["No usable records were returned for this request."]
            ),
            "human_review_required": True,
        },
    }
    """Return the response envelope expected by the coordination console."""
    agent_name = agent_result.get("agent", task)
    return {
        "success": bool(agent_result.get("success", True)),
        "mode": "read_only_self_service",
        "message": message,
        "plan": [{"step": 1, "agent": agent_name, "task": task}],
        "results": [agent_result],
        "decision": {
            "status": "completed" if agent_result.get("success", True) else "unable_to_complete",
            "summary": message,
        },
    }


def _intent_for_employee(query: str):
    """Allow only explicitly recognized, read-only employee requests."""
    q = " ".join(query.lower().strip().split())

    # Deny write/action requests before considering any read intent.
    write_terms = (
        "apply for", "apply leave", "request leave", "take leave",
        "cancel leave", "approve", "reject", "change", "update",
        "edit", "delete", "modify", "mark attendance",
        "correct attendance", "offboard", "terminate", "hire",
        "submit leave", "book leave", "create leave", "withdraw leave",
        "reset password", "change my password",
    )
    if any(term in q for term in write_terms):
        return "blocked"

    profile_terms = (
        "my employee information", "employee information", "my profile",
        "employee profile", "show my details", "my details",
        "my employee details", "show my employee information",
    )
    balance_terms = (
        "leave balance", "my leave balance", "remaining leaves",
        "leaves remaining", "how many leaves", "leave entitlement",
    )
    history_terms = (
        "leave history", "my leave history", "past leaves",
        "previous leave", "leave requests history",
    )
    attendance_terms = (
        "attendance summary", "my attendance", "attendance record",
        "attendance history", "attendance percentage",
    )
    policy_terms = (
        "policy", "policies", "rule", "rules", "work from home", "wfh",
        "remote work", "remote working", "working hours", "benefits",
        "conduct", "remote access", "information security", "holiday",
        "holidays", "leave entitlement", "leave procedure",
    )

    if any(term in q for term in profile_terms):
        return "profile"
    if any(term in q for term in balance_terms):
        return "leave_balance"
    if any(term in q for term in history_terms):
        return "leave_history"
    if any(term in q for term in attendance_terms):
        return "attendance"
    if any(term in q for term in policy_terms):
        return "policy"
    return "unsupported"


@app.post("/api/workflow")
def execute_workflow(
    request: HRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = str(current_user.role).upper()

    if role == "EMPLOYEE":
        linked_employee_id = current_user.employee_id
        if not linked_employee_id:
            raise HTTPException(
                status_code=403,
                detail="Your account is not linked to an employee record.",
            )

        # Never trust the employee_id sent by the browser.
        if linked_employee_id != request.employee_id:
            raise HTTPException(
                status_code=403,
                detail="Employees can only access their own employee information.",
            )

        query = request.request.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Please enter a request.")

        intent = _intent_for_employee(query)
        if intent == "blocked":
            raise HTTPException(
                status_code=403,
                detail=(
            "Submitting or modifying HR records is not available through "
            "the employee self-service interface yet. You can still check "
            "your leave policy, leave balance, and leave history. "
            "Please use your organization's approved process to submit "
            "a leave application."
        ),
    )
        if intent == "unsupported":
            raise HTTPException(
                status_code=403,
                detail=(
                    "Employee accounts can view their own profile, leave balance, "
                    "leave history, attendance summary, and HR policies only."
                ),
            )

        # Only read-only methods are exposed to employee accounts.
        if intent == "profile":
            result = employee_agent.get_employee_profile(db, linked_employee_id)
            return _response("Your employee information was retrieved.", result, "employee profile lookup")

        if intent == "leave_balance":
            result = leave_agent.get_leave_balance(db, linked_employee_id)
            return _response("Your leave balance was retrieved.", result, "leave balance lookup")

        if intent == "leave_history":
            result = leave_agent.get_leave_history(db, linked_employee_id)
            return _response("Your leave history was retrieved.", result, "leave history lookup")

        if intent == "attendance":
            result = attendance_agent.get_attendance_summary(db, linked_employee_id)
            return _response("Your attendance summary was retrieved.", result, "attendance summary lookup")

        if intent == "policy":
            result = policy_agent.search_policy(db=db, keyword=query)
            return _response("The HR policy search has completed.", result, "HR policy search")

    if role != "HR":
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to execute workflows.",
        )

    # Preserve existing HR workflow functionality.
    return workflow_service.execute(
        db=db,
        employee_id=request.employee_id,
        request=request.request,
    )


@app.get("/api/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    return dashboard_service.get_overview(db)
