from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Employee

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


@router.get("/")
def get_employees(db: Session = Depends(get_db)):
    employees = (
        db.query(Employee)
        .order_by(Employee.id)
        .all()
    )

    return {
        "success": True,
        "count": len(employees),
        "employees": [
            {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "name": f"{employee.first_name} {employee.last_name}",
                "email": employee.email,
                "phone": employee.phone,
                "date_of_birth": str(employee.date_of_birth),
                "joining_date": str(employee.joining_date),
                "department_id": employee.department_id,
                "designation_id": employee.designation_id,
                "employment_type": employee.employment_type,
                "employment_status": employee.employment_status
            }
            for employee in employees
        ]
    }


@router.get("/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
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
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "name": f"{employee.first_name} {employee.last_name}",
            "email": employee.email,
            "phone": employee.phone,
            "date_of_birth": str(employee.date_of_birth),
            "joining_date": str(employee.joining_date),
            "department_id": employee.department_id,
            "designation_id": employee.designation_id,
            "employment_type": employee.employment_type,
            "employment_status": employee.employment_status
        }
    }