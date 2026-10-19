from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    OnboardingRecord,
    OffboardingRecord,
    User
)
from app.auth.dependencies import get_current_user, require_hr


router = APIRouter(
    prefix="/api/lifecycle",
    tags=["Employee Lifecycle"]
)


def authorize_lifecycle_access(
    employee_id: int,
    current_user: User
):
    """Allow HR to view any record and employees only their own."""

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
                detail="Lifecycle information not found."
            )

    elif role != "HR":
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to view lifecycle information."
        )


# =========================================================
# ONBOARDING
# =========================================================

@router.get("/onboarding")
def get_onboarding_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can view all onboarding records."""

    records = (
        db.query(OnboardingRecord)
        .order_by(OnboardingRecord.id.desc())
        .all()
    )

    return {
        "success": True,
        "count": len(records),
        "records": [
            {
                "id": record.id,
                "employee_id": record.employee_id,
                "joining_date": (
                    str(record.joining_date)
                    if record.joining_date else None
                ),
                "documentation_status": record.documentation_status,
                "equipment_status": record.equipment_status,
                "orientation_status": record.orientation_status,
                "overall_status": record.overall_status
            }
            for record in records
        ]
    }


@router.get("/onboarding/{employee_id}")
def get_employee_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return onboarding information only to authorized users."""

    authorize_lifecycle_access(employee_id, current_user)

    record = (
        db.query(OnboardingRecord)
        .filter(OnboardingRecord.employee_id == employee_id)
        .first()
    )

    if not record:
        return {
            "success": True,
            "employee_id": employee_id,
            "record": None
        }

    return {
        "success": True,
        "employee_id": employee_id,
        "record": {
            "id": record.id,
            "joining_date": (
                str(record.joining_date)
                if record.joining_date else None
            ),
            "documentation_status": record.documentation_status,
            "equipment_status": record.equipment_status,
            "orientation_status": record.orientation_status,
            "overall_status": record.overall_status
        }
    }


# =========================================================
# OFFBOARDING
# =========================================================

@router.get("/offboarding")
def get_offboarding_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can view all offboarding records."""

    records = (
        db.query(OffboardingRecord)
        .order_by(OffboardingRecord.id.desc())
        .all()
    )

    return {
        "success": True,
        "count": len(records),
        "records": [
            {
                "id": record.id,
                "employee_id": record.employee_id,
                "status": record.overall_status,
                "resignation_date": (
                    str(record.resignation_date)
                    if record.resignation_date else None
                ),
                "last_working_date": (
                    str(record.last_working_date)
                    if record.last_working_date else None
                )
            }
            for record in records
        ]
    }


@router.get("/offboarding/{employee_id}")
def get_employee_offboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return offboarding information only to authorized users."""

    authorize_lifecycle_access(employee_id, current_user)

    record = (
        db.query(OffboardingRecord)
        .filter(OffboardingRecord.employee_id == employee_id)
        .first()
    )

    if not record:
        return {
            "success": True,
            "employee_id": employee_id,
            "record": None
        }

    return {
        "success": True,
        "employee_id": employee_id,
        "record": {
            "id": record.id,
            "status": record.overall_status,
            "resignation_date": (
                str(record.resignation_date)
                if record.resignation_date else None
            ),
            "last_working_date": (
                str(record.last_working_date)
                if record.last_working_date else None
            )
        }
    }