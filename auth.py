import sqlite3
from werkzeug.security import check_password_hash

DATABASE = "database/employees.db"


def get_employee_by_id(employee_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        employee = conn.execute(
            """
            SELECT employee_id, name, department, designation,
                   email, joining_date, manager_id
            FROM employees
            WHERE employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        return dict(employee) if employee else None

    finally:
        conn.close()


def authenticate_employee(employee_id, password):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        credential = conn.execute(
            """
            SELECT employee_id, password_hash
            FROM employee_credentials
            WHERE employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        if not credential:
            return None

        if not check_password_hash(
            credential["password_hash"],
            password
        ):
            return None

        return get_employee_by_id(employee_id)

    finally:
        conn.close()