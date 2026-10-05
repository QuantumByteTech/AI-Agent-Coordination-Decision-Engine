from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    Employee,
    LeaveRequest,
    Attendance,
    WorkflowExecution,
    AgentActivityLog,
)


class DashboardService:

    def get_overview(self, db: Session) -> dict:

        total_employees = (
            db.query(func.count(Employee.id))
            .scalar()
        )

        active_employees = (
            db.query(func.count(Employee.id))
            .filter(
                Employee.employment_status == "Active"
            )
            .scalar()
        )

        total_leave_requests = (
            db.query(func.count(LeaveRequest.id))
            .scalar()
        )

        pending_leave_requests = (
            db.query(func.count(LeaveRequest.id))
            .filter(
                LeaveRequest.status == "Pending"
            )
            .scalar()
        )

        total_attendance = (
            db.query(func.count(Attendance.id))
            .scalar()
        )

        total_workflows = (
            db.query(func.count(WorkflowExecution.id))
            .scalar()
        )

        completed_workflows = (
            db.query(func.count(WorkflowExecution.id))
            .filter(
                WorkflowExecution.status == "COMPLETED"
            )
            .scalar()
        )

        failed_workflows = (
            db.query(func.count(WorkflowExecution.id))
            .filter(
                WorkflowExecution.status == "FAILED"
            )
            .scalar()
        )

        total_agent_activities = (
            db.query(func.count(AgentActivityLog.id))
            .scalar()
        )

        return {
            "employees": {
                "total": total_employees,
                "active": active_employees,
            },
            "leave": {
                "total_requests": total_leave_requests,
                "pending_requests": pending_leave_requests,
            },
            "attendance": {
                "total_records": total_attendance,
            },
            "workflows": {
                "total": total_workflows,
                "completed": completed_workflows,
                "failed": failed_workflows,
            },
            "agent_activity": {
                "total": total_agent_activities,
            },
        }


dashboard_service = DashboardService()