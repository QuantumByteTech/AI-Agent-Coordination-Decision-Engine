from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    OnboardingRecord,
    OffboardingRecord
)


router = APIRouter(
    prefix="/api/lifecycle",
    tags=["Employee Lifecycle"]
)


# =========================================================
# ONBOARDING
# =========================================================

@router.get("/onboarding")
def get_onboarding_records(
    db: Session = Depends(get_db)
):
    """
    Return employee onboarding records.
    """

    records = (
        db.query(OnboardingRecord)
        .order_by(
            OnboardingRecord.id.desc()
        )
        .all()
    )

    return {
        "success": True,
        "count": len(records),
        "records": [
            {
                "id": record.id,
                "employee_id": record.employee_id,
                "status": record.status,
                "start_date": (
                    str(record.start_date)
                    if record.start_date
                    else None
                ),
                "completion_date": (
                    str(record.completion_date)
                    if record.completion_date
                    else None
                )
            }
            for record in records
        ]
    }


@router.get("/onboarding/{employee_id}")
def get_employee_onboarding(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Return onboarding information for one employee.
    """

    record = (
        db.query(OnboardingRecord)
        .filter(
            OnboardingRecord.employee_id == employee_id
        )
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
            "status": record.status,
            "start_date": (
                str(record.start_date)
                if record.start_date
                else None
            ),
            "completion_date": (
                str(record.completion_date)
                if record.completion_date
                else None
            )
        }
    }


# =========================================================
# OFFBOARDING
# =========================================================

@router.get("/offboarding")
def get_offboarding_records(
    db: Session = Depends(get_db)
):
    """
    Return employee offboarding records.
    """

    records = (
        db.query(OffboardingRecord)
        .order_by(
            OffboardingRecord.id.desc()
        )
        .all()
    )

    return {
        "success": True,
        "count": len(records),
        "records": [
            {
                "id": record.id,
                "employee_id": record.employee_id,
                "status": record.status,
                "resignation_date": (
                    str(record.resignation_date)
                    if record.resignation_date
                    else None
                ),
                "last_working_date": (
                    str(record.last_working_date)
                    if record.last_working_date
                    else None
                )
            }
            for record in records
        ]
    }


@router.get("/offboarding/{employee_id}")
def get_employee_offboarding(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Return offboarding information for one employee.
    """

    record = (
        db.query(OffboardingRecord)
        .filter(
            OffboardingRecord.employee_id == employee_id
        )
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
            "status": record.status,
            "resignation_date": (
                str(record.resignation_date)
                if record.resignation_date
                else None
            ),
            "last_working_date": (
                str(record.last_working_date)
                if record.last_working_date
                else None
            )
        }
    }