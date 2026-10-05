from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import LeaveRequest, LeaveBalance


router = APIRouter(
    prefix="/api/leaves",
    tags=["Leave Management"]
)


@router.get("/employee/{employee_id}")
def get_employee_leaves(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Return leave balance and leave history for an employee.
    """

    balance = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.employee_id == employee_id
        )
        .first()
    )

    requests = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id
        )
        .order_by(
            LeaveRequest.start_date.desc()
        )
        .all()
    )

    return {
        "success": True,
        "employee_id": employee_id,
        "leave_balance": (
            {
                "casual_leave": balance.casual_leave,
                "sick_leave": balance.sick_leave,
                "vacation_leave": balance.vacation_leave
            }
            if balance
            else None
        ),
        "leave_requests": [
            {
                "id": request.id,
                "leave_type": request.leave_type,
                "start_date": str(request.start_date),
                "end_date": str(request.end_date),
                "status": request.status,
                "reason": request.reason
            }
            for request in requests
        ]
    }


@router.get("/pending")
def get_pending_leaves(
    db: Session = Depends(get_db)
):
    """
    Return pending leave requests for HR review.
    """

    requests = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Pending"
        )
        .order_by(
            LeaveRequest.start_date.asc()
        )
        .all()
    )

    return {
        "success": True,
        "count": len(requests),
        "requests": [
            {
                "id": request.id,
                "employee_id": request.employee_id,
                "leave_type": request.leave_type,
                "start_date": str(request.start_date),
                "end_date": str(request.end_date),
                "status": request.status,
                "reason": request.reason
            }
            for request in requests
        ]
    }


@router.put("/{leave_id}/approve")
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db)
):
    """
    Approve a pending leave request.
    """

    request = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found."
        )

    if request.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be approved."
        )

    request.status = "Approved"

    db.commit()
    db.refresh(request)

    return {
        "success": True,
        "message": "Leave request approved.",
        "leave_id": request.id,
        "status": request.status
    }


@router.put("/{leave_id}/reject")
def reject_leave(
    leave_id: int,
    db: Session = Depends(get_db)
):
    """
    Reject a pending leave request.
    """

    request = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found."
        )

    if request.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be rejected."
        )

    request.status = "Rejected"

    db.commit()
    db.refresh(request)

    return {
        "success": True,
        "message": "Leave request rejected.",
        "leave_id": request.id,
        "status": request.status
    }