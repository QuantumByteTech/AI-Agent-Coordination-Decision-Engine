from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.department_api import router as department_router

from app.database.database import get_db
from app.database.models import User
from app.auth.dependencies import get_current_user, require_hr
from app.services.workflow_service import workflow_service
from app.services.dashboard_service import dashboard_service
from app.agents.policy_agent import policy_agent

from app.api.employee_api import router as employee_router
from app.api.leave_api import router as leave_router
from app.api.attendance_api import router as attendance_router
from app.api.lifecycle_api import router as lifecycle_router
from app.api.workflow_api import router as workflow_router
from app.api.agent_api import router as agent_router
from app.api.auth_api import router as auth_router


app = FastAPI(
    title="AI Agent Coordination & Decision Engine",
    description=(
        "Enterprise HR workflow automation, "
        "multi-agent coordination and decision support platform."
    ),
    version="1.0.0"
)


# CORS configuration
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


# Router registration
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


@app.get("/")
def root():
    return {
        "success": True,
        "system": "AI Agent Coordination & Decision Engine",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/workflow")
def execute_workflow(
    request: HRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = str(current_user.role).upper()

    # Employee access: policy questions only, no workflow execution.
    if role == "EMPLOYEE":

        if not current_user.employee_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Your account is not linked "
                    "to an employee record."
                )
            )

        if current_user.employee_id != request.employee_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Employees can only access "
                    "their own employee information."
                )
            )

        query = request.request.strip()

        if not query:
            raise HTTPException(
                status_code=400,
                detail="Please enter an HR policy question."
            )

        normalized_query = query.lower()

        # Employees may submit only their own leave request, read their own
        # HR information, or ask HR policy questions. The employee_id is
        # always checked against the authenticated account above.
        leave_request_terms = (
            "apply for leave", "apply leave", "request leave",
            "take leave", "book leave", "submit leave",
            "i need leave", "i want leave", "i would like leave",
            "leave request", "requesting leave"
        )
        personal_info_terms = (
            "my employee information", "show my employee information",
            "my profile", "my leave balance", "my leave history",
            "my attendance", "my employee record", "my information"
        )
        policy_terms = (
            "policy", "policies", "rule", "rules", "work from home",
            "wfh", "working hours", "benefits", "conduct",
            "remote access", "information security", "holiday",
            "holidays", "leave policy", "attendance policy",
            "company policy", "approval requirements", "approval process"
        )
        sensitive_action_terms = (
            "approve leave", "approve request", "reject leave",
            "reject request", "cancel leave", "change my balance",
            "update my record", "edit my record", "delete my record",
            "modify my record", "mark attendance", "correct attendance",
            "offboard", "terminate", "hire", "assign employee",
            "change department", "set target"
        )

        if any(term in normalized_query for term in sensitive_action_terms):
            raise HTTPException(
                status_code=403,
                detail="Employee accounts cannot approve, reject, cancel, or administer HR records."
            )

        is_leave_request = any(term in normalized_query for term in leave_request_terms)
        is_personal_info = any(term in normalized_query for term in personal_info_terms)
        is_policy_question = any(term in normalized_query for term in policy_terms)

        if is_leave_request or is_personal_info:
            # Route only the authenticated employee's own request through the
            # existing coordinator. The request cannot select another employee.
            return workflow_service.execute(
                db=db,
                employee_id=current_user.employee_id,
                request=query
            )

        if is_policy_question:
            result = policy_agent.search_policy(db=db, keyword=query)
            return {
                "success": True,
                "mode": "read_only_policy",
                "result": result
            }

        raise HTTPException(
            status_code=403,
            detail=(
                "Employees may ask HR policy questions, view their own HR "
                "information, or submit a leave request. Other HR actions are restricted."
            )
        )

    # Reject unknown or unsupported roles.
    if role != "HR":
        raise HTTPException(
            status_code=403,
            detail=(
                "Your account is not authorized "
                "to execute workflows."
            )
        )

    # Preserve existing HR workflow functionality.
    return workflow_service.execute(
        db=db,
        employee_id=request.employee_id,
        request=request.request
    )


@app.get("/api/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    return dashboard_service.get_overview(db)