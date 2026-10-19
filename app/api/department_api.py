from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import require_hr
from app.database.database import get_db
from app.database.models import Department, Employee, User

router = APIRouter(
    prefix="/api/departments",
    tags=["Departments"],
)


class TargetHeadcountUpdate(BaseModel):
    target_headcount: int = Field(ge=0)


class EmployeeDepartmentUpdate(BaseModel):
    department_id: int = Field(gt=0)


def serialize_department(db: Session, department: Department) -> dict:
    total_employees = (
        db.query(Employee)
        .filter(Employee.department_id == department.id)
        .count()
    )

    active_employees = (
        db.query(Employee)
        .filter(
            Employee.department_id == department.id,
            Employee.employment_status == "Active",
        )
        .count()
    )

    target = department.target_headcount

    return {
        "id": department.id,
        "name": department.name,
        "location": department.location,
        "target_headcount": target,
        "total_employees": total_employees,
        "active_headcount": active_employees,
        "hiring_gap": max(target - active_employees, 0),
        "over_target": max(active_employees - target, 0),
    }


@router.get("/")
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    departments = (
        db.query(Department)
        .order_by(Department.name)
        .all()
    )

    return [
        serialize_department(db, department)
        for department in departments
    ]


@router.put("/{department_id}/target")
def update_department_target(
    department_id: int,
    payload: TargetHeadcountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found.",
        )

    department.target_headcount = payload.target_headcount

    try:
        db.commit()
        db.refresh(department)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update the department target.",
        )

    return serialize_department(db, department)


@router.put("/assignments/{employee_id}")
def assign_employee_department(
    employee_id: int,
    payload: EmployeeDepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found.",
        )

    department = (
        db.query(Department)
        .filter(Department.id == payload.department_id)
        .first()
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found.",
        )

    employee.department_id = department.id

    try:
        db.commit()
        db.refresh(employee)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to assign the employee to the department.",
        )

    return {
        "message": "Employee department updated successfully.",
        "employee_id": employee.id,
        "department_id": department.id,
        "department_name": department.name,
    }