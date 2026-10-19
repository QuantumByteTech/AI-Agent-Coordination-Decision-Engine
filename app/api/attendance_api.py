from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Attendance, User
from app.auth.dependencies import get_current_user, require_hr


router = APIRouter(
    prefix="/api/attendance",
    tags=["Attendance"]
)


def authorize_employee_access(
    employee_id: int,
    current_user: User
):
    """Allow HR to access any employee; employees only their own records."""

    role = str(current_user.role).upper()

    if role == "EMPLOYEE":
        if not current_user.employee_id:
            raise HTTPException(
                status_code=403,
                detail="Your account is not linked to an employee record."
            )

        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=404,
                detail="Attendance information not found."
            )

    elif role != "HR":
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to view attendance."
        )


@router.get("/employee/{employee_id}")
def get_employee_attendance(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return attendance history for the authorized employee."""

    authorize_employee_access(employee_id, current_user)

    records = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id)
        .order_by(Attendance.attendance_date.desc())
        .all()
    )

    return {
        "success": True,
        "employee_id": employee_id,
        "count": len(records),
        "attendance": [
            {
                "id": record.id,
                "date": (
                    str(record.attendance_date)
                    if record.attendance_date else None
                ),
                "status": record.status,
                "check_in": (
                    str(record.check_in)
                    if record.check_in else None
                ),
                "check_out": (
                    str(record.check_out)
                    if record.check_out else None
                )
            }
            for record in records
        ]
    }


@router.get("/summary/{employee_id}")
def get_attendance_summary(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return attendance statistics for the authorized employee."""

    authorize_employee_access(employee_id, current_user)

    records = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id)
        .all()
    )

    total = len(records)

    present = sum(
        1 for record in records
        if record.status == "Present"
    )

    absent = sum(
        1 for record in records
        if record.status == "Absent"
    )

    late = sum(
        1 for record in records
        if record.status == "Late"
    )

    return {
        "success": True,
        "employee_id": employee_id,
        "summary": {
            "total_records": total,
            "present": present,
            "absent": absent,
            "late": late,
            "attendance_percentage": (
                round((present / total) * 100, 2)
                if total else 0
            )
        }
    }


@router.get("/recent")
def get_recent_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can view recent attendance across employees."""

    records = (
        db.query(Attendance)
        .order_by(Attendance.attendance_date.desc())
        .limit(100)
        .all()
    )

    return {
        "success": True,
        "count": len(records),
        "attendance": [
            {
                "id": record.id,
                "employee_id": record.employee_id,
                "date": (
                    str(record.attendance_date)
                    if record.attendance_date else None
                ),
                "status": record.status,
                "check_in": (
                    str(record.check_in)
                    if record.check_in else None
                ),
                "check_out": (
                    str(record.check_out)
                    if record.check_out else None
                )
            }
            for record in records
        ]
    }