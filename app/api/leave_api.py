from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import LeaveRequest, LeaveBalance, User
from app.auth.dependencies import get_current_user, require_hr


router = APIRouter(
    prefix="/api/leaves",
    tags=["Leave Management"]
)


@router.get("/employee/{employee_id}")
def get_employee_leaves(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Employees can view their own leave details; HR can view any employee."""

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
                detail="Leave information not found."
            )

    elif role != "HR":
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to view leave information."
        )

    balance = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id)
        .first()
    )

    requests = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.employee_id == employee_id)
        .order_by(LeaveRequest.start_date.desc())
        .all()
    )

    return {
        "success": True,
        "employee_id": employee_id,
        "leave_balance": (
            {
                "casual_leave": balance.casual_leave,
                "sick_leave": balance.sick_leave,
                "earned_leave": balance.earned_leave
            }
            if balance
            else None
        ),
        "leave_requests": [
            {
                "id": leave.id,
                "leave_type": leave.leave_type,
                "start_date": (
                    str(leave.start_date)
                    if leave.start_date else None
                ),
                "end_date": (
                    str(leave.end_date)
                    if leave.end_date else None
                ),
                "status": leave.status,
                "reason": leave.reason
            }
            for leave in requests
        ]
    }


@router.get("/pending")
def get_pending_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can view all pending leave requests."""

    requests = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.status == "Pending")
        .order_by(LeaveRequest.start_date.asc())
        .all()
    )

    return {
        "success": True,
        "count": len(requests),
        "requests": [
            {
                "id": leave.id,
                "employee_id": leave.employee_id,
                "leave_type": leave.leave_type,
                "start_date": (
                    str(leave.start_date)
                    if leave.start_date else None
                ),
                "end_date": (
                    str(leave.end_date)
                    if leave.end_date else None
                ),
                "status": leave.status,
                "reason": leave.reason
            }
            for leave in requests
        ]
    }


@router.put("/{leave_id}/approve")
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can approve a pending leave request."""

    leave = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found."
        )

    if leave.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be approved."
        )

    leave.status = "Approved"

    db.commit()
    db.refresh(leave)

    return {
        "success": True,
        "message": "Leave request approved.",
        "leave_id": leave.id,
        "status": leave.status
    }


@router.put("/{leave_id}/reject")
def reject_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can reject a pending leave request."""

    leave = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found."
        )

    if leave.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be rejected."
        )

    leave.status = "Rejected"

    db.commit()
    db.refresh(leave)

    return {
        "success": True,
        "message": "Leave request rejected.",
        "leave_id": leave.id,
        "status": leave.status
    }