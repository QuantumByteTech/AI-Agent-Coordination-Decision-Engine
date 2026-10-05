import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import WorkflowExecution
from app.workflows.hr_workflow import hr_workflow
from app.memory.memory_manager import memory_manager
from app.utils.agent_logger import log_agent_activity


class WorkflowService:
    """
    Enterprise workflow execution service.

    Responsible for:
    - Creating workflow IDs
    - Executing the coordinated agent workflow
    - Recording workflow status
    - Updating conversational memory
    - Recording agent activity
    """

    def execute(
        self,
        db: Session,
        employee_id: int,
        request: str
    ) -> dict:

        workflow_id = str(uuid.uuid4())

        workflow_record = WorkflowExecution(
            workflow_id=workflow_id,
            employee_id=employee_id,
            request=request,
            status="RUNNING",
            started_at=datetime.now()
        )

        db.add(workflow_record)
        db.commit()

        memory_manager.add_message(
            employee_id=employee_id,
            role="employee",
            content=request
        )

        log_agent_activity(
            db=db,
            workflow_id=workflow_id,
            agent_name="AI HR Coordinator",
            action="Workflow started",
            status="STARTED",
            details=request
        )

        try:

            state = {
                "employee_id": employee_id,
                "request": request,
                "db": db
            }

            result = hr_workflow.invoke(state)

            if result.get("error"):

                workflow_record.status = "FAILED"
                workflow_record.completed_at = datetime.now()

                db.commit()

                log_agent_activity(
                    db=db,
                    workflow_id=workflow_id,
                    agent_name="AI HR Coordinator",
                    action="Workflow execution",
                    status="FAILED",
                    details=result["error"]
                )

                return {
                    "success": False,
                    "workflow_id": workflow_id,
                    "error": result["error"]
                }

            decision = result.get(
                "decision",
                {}
            )

            memory_manager.store_workflow(
                employee_id=employee_id,
                request=request,
                decision=decision
            )

            memory_manager.add_message(
                employee_id=employee_id,
                role="system",
                content=str(decision)
            )

            workflow_record.status = "COMPLETED"
            workflow_record.completed_at = datetime.now()

            db.commit()

            log_agent_activity(
                db=db,
                workflow_id=workflow_id,
                agent_name="AI HR Coordinator",
                action="Workflow execution",
                status="COMPLETED",
                details=str(decision)
            )

            return {
                "success": True,
                "workflow_id": workflow_id,
                "request": request,
                "plan": result.get("plan", []),
                "results": result.get("results", []),
                "decision": decision
            }

        except Exception as exc:

            workflow_record.status = "FAILED"
            workflow_record.completed_at = datetime.now()

            db.commit()

            log_agent_activity(
                db=db,
                workflow_id=workflow_id,
                agent_name="AI HR Coordinator",
                action="Workflow execution",
                status="ERROR",
                details=str(exc)
            )

            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": (
                    "Workflow execution failed."
                ),
                "details": str(exc)
            }


workflow_service = WorkflowService()