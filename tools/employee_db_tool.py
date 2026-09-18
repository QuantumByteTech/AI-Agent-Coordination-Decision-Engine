import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "employees.db"


def get_employee_info(employee_id: str):

    if not employee_id:
        return {
            "success": False,
            "error": "Employee ID is required."
        }

    employee_id = str(employee_id).strip()

    if not employee_id.isdigit():
        return {
            "success": False,
            "error": "Employee ID must contain only numbers."
        }

    try:

        connection = sqlite3.connect(DB_PATH)

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                employee_id,
                name,
                department,
                designation,
                email,
                joining_date
            FROM employees
            WHERE employee_id = ?
        """, (int(employee_id),))

        employee = cursor.fetchone()

        connection.close()

        if employee is None:
            return {
                "success": False,
                "error": f"Employee ID {employee_id} was not found."
            }

        return {
            "success": True,
            "employee_id": employee["employee_id"],
            "name": employee["name"],
            "department": employee["department"],
            "designation": employee["designation"],
            "email": employee["email"],
            "joining_date": employee["joining_date"]
        }

    except sqlite3.Error:
        return {
            "success": False,
            "error": "Unable to access employee database."
        }