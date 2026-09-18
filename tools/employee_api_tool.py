import sqlite3
import os


def get_employee_info(employee_id: str):
    """
    Retrieve employee information from the local SQLite database.
    """

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

    # Locate employees.db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "database", "employees.db")

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT employee_id, name, department, email
            FROM employees
            WHERE employee_id = ?
            """,
            (int(employee_id),)
        )

        employee = cursor.fetchone()

        connection.close()

        if not employee:
            return {
                "success": False,
                "error": f"Employee ID {employee_id} was not found."
            }

        return {
            "success": True,
            "employee_id": employee[0],
            "name": employee[1],
            "department": employee[2],
            "email": employee[3]
        }

    except sqlite3.Error as e:
        return {
            "success": False,
            "error": "Unable to access the employee database."
        }