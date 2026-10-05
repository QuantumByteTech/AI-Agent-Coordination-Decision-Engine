from sqlalchemy.orm import Session

from app.database.models import (
    Employee,
    Department,
    Designation,
    LeaveBalance,
    LeaveRequest,
    Attendance,
    HRRequest,
    OnboardingRecord,
    OffboardingRecord,
    HRPolicy,
    WorkflowExecution,
    AgentActivityLog,
)


class EmployeeRepository:

    @staticmethod
    def get_by_id(db: Session, employee_id: int):
        return (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session):
        return db.query(Employee).all()

    @staticmethod
    def search(db: Session, keyword: str):
        pattern = f"%{keyword}%"

        return (
            db.query(Employee)
            .filter(
                (Employee.first_name.ilike(pattern))
                | (Employee.last_name.ilike(pattern))
                | (Employee.email.ilike(pattern))
            )
            .all()
        )


class LeaveRepository:

    @staticmethod
    def get_balance(db: Session, employee_id: int):
        return (
            db.query(LeaveBalance)
            .filter(LeaveBalance.employee_id == employee_id)
            .first()
        )

    @staticmethod
    def get_requests(db: Session, employee_id: int):
        return (
            db.query(LeaveRequest)
            .filter(LeaveRequest.employee_id == employee_id)
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )

    @staticmethod
    def get_all_requests(db: Session):
        return (
            db.query(LeaveRequest)
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )


class AttendanceRepository:

    @staticmethod
    def get_employee_attendance(db: Session, employee_id: int):
        return (
            db.query(Attendance)
            .filter(Attendance.employee_id == employee_id)
            .order_by(Attendance.date.desc())
            .all()
        )

    @staticmethod
    def get_all_attendance(db: Session):
        return (
            db.query(Attendance)
            .order_by(Attendance.date.desc())
            .all()
        )


class HRRequestRepository:

    @staticmethod
    def get_by_employee(db: Session, employee_id: int):
        return (
            db.query(HRRequest)
            .filter(HRRequest.employee_id == employee_id)
            .order_by(HRRequest.created_at.desc())
            .all()
        )

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(HRRequest)
            .order_by(HRRequest.created_at.desc())
            .all()
        )


class PolicyRepository:

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(HRPolicy)
            .order_by(HRPolicy.category)
            .all()
        )

    @staticmethod
    def search(db: Session, keyword: str):
        pattern = f"%{keyword}%"

        return (
            db.query(HRPolicy)
            .filter(
                (HRPolicy.title.ilike(pattern))
                | (HRPolicy.content.ilike(pattern))
                | (HRPolicy.category.ilike(pattern))
            )
            .all()
        )


class OnboardingRepository:

    @staticmethod
    def get_by_employee(db: Session, employee_id: int):
        return (
            db.query(OnboardingRecord)
            .filter(OnboardingRecord.employee_id == employee_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session):
        return db.query(OnboardingRecord).all()


class OffboardingRepository:

    @staticmethod
    def get_by_employee(db: Session, employee_id: int):
        return (
            db.query(OffboardingRecord)
            .filter(OffboardingRecord.employee_id == employee_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session):
        return db.query(OffboardingRecord).all()


class WorkflowRepository:

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(WorkflowExecution)
            .order_by(WorkflowExecution.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, workflow_id: int):
        return (
            db.query(WorkflowExecution)
            .filter(WorkflowExecution.id == workflow_id)
            .first()
        )


class AgentActivityRepository:

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(AgentActivityLog)
            .order_by(AgentActivityLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_recent(db: Session, limit: int = 50):
        return (
            db.query(AgentActivityLog)
            .order_by(AgentActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )