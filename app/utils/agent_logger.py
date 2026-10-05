from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import AgentActivityLog


def log_agent_activity(
    db: Session,
    workflow_id: str,
    agent_name: str,
    action: str,
    status: str,
    details: str = ""
):
    """
    Store an agent activity in the enterprise activity log.
    """

    activity = AgentActivityLog(
        workflow_id=workflow_id,
        agent_name=agent_name,
        action=action,
        status=status,
        details=details,
        timestamp=datetime.now()
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


def get_workflow_activity(
    db: Session,
    workflow_id: str
):
    """
    Retrieve all agent activities belonging to a workflow.
    """

    return (
        db.query(AgentActivityLog)
        .filter(
            AgentActivityLog.workflow_id == workflow_id
        )
        .order_by(
            AgentActivityLog.timestamp.asc()
        )
        .all()
    )