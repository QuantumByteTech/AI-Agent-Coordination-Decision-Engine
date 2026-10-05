from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Attendance


router = APIRouter(
    prefix="/api/attendance",
    tags=["Attendance"]
)


@router.get("/employee/{employee_id}")
def get_employee_attendance(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Return attendance history for an employee.
    """

    records = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id
        )
        .order_by(
            Attendance.date.desc()
        )
        .all()
    )

    return {
        "success": True,
        "employee_id": employee_id,
        "count": len(records),
        "attendance": [
            {
                "id": record.id,
                "date": str(record.date),
                "status": record.status,
                "check_in": str(record.check_in)
                if record.check_in else None,
                "check_out": str(record.check_out)
                if record.check_out else None
            }
            for record in records
        ]
    }


@router.get("/summary/{employee_id}")
def get_attendance_summary(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Return attendance statistics for an employee.
    """

    records = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id
        )
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
                if total
                else 0
            )
        }
    }


@router.get("/recent")
def get_recent_attendance(
    db: Session = Depends(get_db)
):
    """
    Return recent attendance records for HR monitoring.
    """

    records = (
        db.query(Attendance)
        .order_by(
            Attendance.date.desc()
        )
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
                "date": str(record.date),
                "status": record.status,
                "check_in": str(record.check_in)
                if record.check_in else None,
                "check_out": str(record.check_out)
                if record.check_out else None
            }
            for record in records
        ]
    }