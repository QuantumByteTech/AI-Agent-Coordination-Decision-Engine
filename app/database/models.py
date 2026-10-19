from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)

    target_headcount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

class Designation(Base):
    __tablename__ = "designations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )

    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )

    designation_id: Mapped[int] = mapped_column(
        ForeignKey("designations.id"), nullable=False
    )

    employment_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    employment_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Active"
    )

    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )

    salary: Mapped[float] = mapped_column(Float, nullable=False)


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    casual_leave: Mapped[float] = mapped_column(Float, default=12)
    sick_leave: Mapped[float] = mapped_column(Float, default=10)
    earned_leave: Mapped[float] = mapped_column(Float, default=15)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    leave_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Pending"
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    check_in: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    check_out: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )


class HRRequest(Base):
    __tablename__ = "hr_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    request_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)

    priority: Mapped[str] = mapped_column(
        String(30), default="Medium"
    )

    status: Mapped[str] = mapped_column(
        String(30), default="Open"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class OnboardingRecord(Base):
    __tablename__ = "onboarding_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    joining_date: Mapped[date] = mapped_column(Date, nullable=False)

    documentation_status: Mapped[str] = mapped_column(
        String(30), default="Pending"
    )

    equipment_status: Mapped[str] = mapped_column(
        String(30), default="Pending"
    )

    orientation_status: Mapped[str] = mapped_column(
        String(30), default="Pending"
    )

    overall_status: Mapped[str] = mapped_column(
        String(30), default="In Progress"
    )


class OffboardingRecord(Base):
    __tablename__ = "offboarding_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    resignation_date: Mapped[date] = mapped_column(Date, nullable=False)

    last_working_date: Mapped[date] = mapped_column(Date, nullable=False)

    exit_interview_status: Mapped[str] = mapped_column(
        String(30), default="Pending"
    )

    asset_return_status: Mapped[str] = mapped_column(
        String(30), default="Pending"
    )

    clearance_status: Mapped[str] = mapped_column(
        String(30), default="Pending"
    )

    overall_status: Mapped[str] = mapped_column(
        String(30), default="In Progress"
    )


class HRPolicy(Base):
    __tablename__ = "hr_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    policy_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )

    workflow_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    decision: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class AgentActivityLog(Base):
    __tablename__ = "agent_activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    workflow_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_executions.id"), nullable=False
    )

    agent_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True, unique=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
