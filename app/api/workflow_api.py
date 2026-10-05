from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import WorkflowExecution


router = APIRouter(
    prefix="/api/workflows",
    tags=["Workflow Monitoring"]
)


@router.get("/")
def get_workflows(
    db: Session = Depends(get_db)
):
    """
    Return recent enterprise workflow executions.
    """

    workflows = (
        db.query(WorkflowExecution)
        .order_by(
            WorkflowExecution.id.desc()
        )
        .limit(100)
        .all()
    )

    return {
        "success": True,
        "count": len(workflows),
        "workflows": [
            {
                "id": workflow.id,
                "workflow_id": workflow.workflow_id,
                "employee_id": workflow.employee_id,
                "request": workflow.request,
                "status": workflow.status,
                "started_at": (
                    str(workflow.started_at)
                    if workflow.started_at
                    else None
                ),
                "completed_at": (
                    str(workflow.completed_at)
                    if workflow.completed_at
                    else None
                )
            }
            for workflow in workflows
        ]
    }


@router.get("/{workflow_id}")
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """
    Return details of a specific workflow execution.
    """

    workflow = (
        db.query(WorkflowExecution)
        .filter(
            WorkflowExecution.workflow_id == workflow_id
        )
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found."
        )

    return {
        "success": True,
        "workflow": {
            "id": workflow.id,
            "workflow_id": workflow.workflow_id,
            "employee_id": workflow.employee_id,
            "request": workflow.request,
            "status": workflow.status,
            "started_at": (
                str(workflow.started_at)
                if workflow.started_at
                else None
            ),
            "completed_at": (
                str(workflow.completed_at)
                if workflow.completed_at
                else None
            )
        }
    }


@router.get("/status/{status}")
def get_workflows_by_status(
    status: str,
    db: Session = Depends(get_db)
):
    """
    Filter workflow executions by status.
    """

    workflows = (
        db.query(WorkflowExecution)
        .filter(
            WorkflowExecution.status == status.upper()
        )
        .order_by(
            WorkflowExecution.id.desc()
        )
        .all()
    )

    return {
        "success": True,
        "status": status.upper(),
        "count": len(workflows),
        "workflows": [
            {
                "workflow_id": workflow.workflow_id,
                "employee_id": workflow.employee_id,
                "request": workflow.request,
                "status": workflow.status,
                "started_at": (
                    str(workflow.started_at)
                    if workflow.started_at
                    else None
                ),
                "completed_at": (
                    str(workflow.completed_at)
                    if workflow.completed_at
                    else None
                )
            }
            for workflow in workflows
        ]
    }