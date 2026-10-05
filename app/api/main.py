from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.workflow_service import workflow_service
from app.services.dashboard_service import dashboard_service

from app.api.employee_api import router as employee_router
from app.api.leave_api import router as leave_router
from app.api.attendance_api import router as attendance_router
from app.api.lifecycle_api import router as lifecycle_router
from app.api.workflow_api import router as workflow_router
from app.api.agent_api import router as agent_router


app = FastAPI(
    title="AI Agent Coordination & Decision Engine",
    description=(
        "Enterprise HR workflow automation, "
        "multi-agent coordination and decision support platform."
    ),
    version="1.0.0"
)


# =========================================================
# ROUTER REGISTRATION
# =========================================================

app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(attendance_router)
app.include_router(lifecycle_router)
app.include_router(workflow_router)
app.include_router(agent_router)


# =========================================================
# REQUEST MODEL
# =========================================================

class HRRequest(BaseModel):
    employee_id: int
    request: str


# =========================================================
# SYSTEM ENDPOINTS
# =========================================================

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


# =========================================================
# AI WORKFLOW
# =========================================================

@app.post("/api/workflow")
def execute_workflow(
    request: HRRequest,
    db: Session = Depends(get_db)
):
    return workflow_service.execute(
        db=db,
        employee_id=request.employee_id,
        request=request.request
    )


# =========================================================
# HR DASHBOARD
# =========================================================

@app.get("/api/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db)
):
    return dashboard_service.get_overview(db)