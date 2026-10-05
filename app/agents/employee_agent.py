from sqlalchemy.orm import Session

from app.database.repository import EmployeeRepository


class EmployeeAgent:
    """
    Specialized agent responsible for employee information
    and employee profile-related requests.
    """

    name = "Employee Intelligence Agent"
    description = (
        "Retrieves and presents employee information from "
        "the enterprise HR database."
    )

    def get_employee_profile(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        employee = EmployeeRepository.get_by_id(
            db,
            employee_id
        )

        if not employee:
            return {
                "success": False,
                "agent": self.name,
                "message": (
                    f"No employee was found with ID {employee_id}."
                )
            }

        return {
            "success": True,
            "agent": self.name,
            "employee": {
                "employee_id": employee.id,
                "employee_code": employee.employee_code,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "phone": employee.phone,
                "department_id": employee.department_id,
                "designation_id": employee.designation_id,
                "employment_status": employee.employment_status,
                "joining_date": str(employee.joining_date),
                "location": employee.location,
            }
        }

    def search_employees(
        self,
        db: Session,
        keyword: str
    ) -> dict:

        employees = EmployeeRepository.search(
            db,
            keyword
        )

        results = []

        for employee in employees:
            results.append({
                "employee_id": employee.id,
                "employee_code": employee.employee_code,
                "name": (
                    f"{employee.first_name} "
                    f"{employee.last_name}"
                ),
                "email": employee.email,
                "employment_status": employee.employment_status,
                "location": employee.location,
            })

        return {
            "success": True,
            "agent": self.name,
            "count": len(results),
            "employees": results
        }


employee_agent = EmployeeAgent()