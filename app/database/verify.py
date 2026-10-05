from sqlalchemy import func

from app.database.database import SessionLocal
from app.database.models import (
    Department,
    Designation,
    Employee,
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


def verify_database():
    db = SessionLocal()

    try:
        print("=" * 60)
        print("NexaCore Technologies Database Verification")
        print("=" * 60)

        tables = [
            ("Departments", Department),
            ("Designations", Designation),
            ("Employees", Employee),
            ("Leave Balances", LeaveBalance),
            ("Leave Requests", LeaveRequest),
            ("Attendance Records", Attendance),
            ("HR Requests", HRRequest),
            ("Onboarding Records", OnboardingRecord),
            ("Offboarding Records", OffboardingRecord),
            ("HR Policies", HRPolicy),
            ("Workflow Executions", WorkflowExecution),
            ("Agent Activity Logs", AgentActivityLog),
        ]

        all_valid = True

        for name, model in tables:
            count = db.query(func.count()).select_from(model).scalar()

            if count > 0:
                print(f"[OK] {name:<25} {count}")
            else:
                print(f"[EMPTY] {name:<25} EMPTY")
                all_valid = False

        print("=" * 60)

        if all_valid:
            print("DATABASE VERIFICATION SUCCESSFUL")
        else:
            print("DATABASE VERIFICATION COMPLETED WITH WARNINGS")

        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    verify_database()