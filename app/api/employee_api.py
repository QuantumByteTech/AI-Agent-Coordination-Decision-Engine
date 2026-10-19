from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Employee, User
from app.auth.dependencies import get_current_user, require_hr


router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


def serialize_employee(employee: Employee) -> dict:
    """Return the employee fields permitted by this API."""
    return {
        "id": employee.id,
        "employee_code": employee.employee_code,
        "name": f"{employee.first_name} {employee.last_name}",
        "email": employee.email,
        "phone": employee.phone,
        "date_of_birth": (
            str(employee.date_of_birth)
            if employee.date_of_birth
            else None
        ),
        "joining_date": (
            str(employee.joining_date)
            if employee.joining_date
            else None
        ),
        "department_id": employee.department_id,
        "designation_id": employee.designation_id,
        "employment_type": employee.employment_type,
        "employment_status": employee.employment_status
    }


@router.get("/")
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """Only HR can view the employee directory."""
    employees = (
        db.query(Employee)
        .order_by(Employee.id)
        .all()
    )

    return {
        "success": True,
        "count": len(employees),
        "employees": [
            serialize_employee(employee)
            for employee in employees
        ]
    }


@router.get("/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HR can view any employee; employees can view only themselves."""

    role = str(current_user.role).upper()

    if role == "EMPLOYEE":
        if not current_user.employee_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Your account is not linked "
                    "to an employee record."
                )
            )

        if current_user.employee_id != employee_id:
            # 404 avoids confirming that another employee ID exists.
            raise HTTPException(
                status_code=404,
                detail="Employee not found."
            )

    elif role != "HR":
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to view employee details."
        )

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return {
        "success": True,
        "employee": serialize_employee(employee)
    }