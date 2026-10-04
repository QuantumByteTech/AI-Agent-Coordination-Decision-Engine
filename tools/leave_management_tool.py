import sqlite3
from pathlib import Path
from datetime import date, datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "employees.db"


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _audit(
    connection,
    actor_id,
    actor_name,
    action,
    entity_type,
    entity_id=None,
    details=None
):
    connection.execute(
        """
        INSERT INTO audit_logs
        (
            actor_id,
            actor_name,
            action,
            entity_type,
            entity_id,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            actor_id,
            actor_name,
            action,
            entity_type,
            entity_id,
            details,
            datetime.now().isoformat(timespec="seconds")
        )
    )


def get_employee_context(employee_id):
    """Return employee and reporting-manager information."""

    try:
        employee_id = int(str(employee_id).strip())
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "Employee ID must be a valid number."
        }

    connection = _connect()

    try:
        row = connection.execute(
            """
            SELECT
                e.employee_id,
                e.name,
                e.department,
                e.designation,
                e.email,
                e.joining_date,
                e.manager_id,
                m.name AS manager_name,
                m.email AS manager_email
            FROM employees e
            LEFT JOIN employees m
                ON e.manager_id = m.employee_id
            WHERE e.employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        if row is None:
            return {
                "success": False,
                "error": f"Employee ID {employee_id} was not found."
            }

        return {
            "success": True,
            "employee_id": row["employee_id"],
            "name": row["name"],
            "department": row["department"],
            "designation": row["designation"],
            "email": row["email"],
            "joining_date": row["joining_date"],
            "manager_id": row["manager_id"],
            "manager_name": row["manager_name"],
            "manager_email": row["manager_email"]
        }

    finally:
        connection.close()


def get_leave_balance(employee_id, year=None):
    """Return the employee's leave balance."""

    year = year or datetime.now().year

    connection = _connect()

    try:
        row = connection.execute(
            """
            SELECT
                employee_id,
                calendar_year,
                casual_leave_total,
                casual_leave_used
            FROM leave_balances
            WHERE employee_id = ?
              AND calendar_year = ?
            """,
            (int(employee_id), year)
        ).fetchone()

        if row is None:
            return {
                "success": False,
                "error": "Leave balance was not found."
            }

        total = row["casual_leave_total"]
        used = row["casual_leave_used"]

        return {
            "success": True,
            "employee_id": row["employee_id"],
            "year": row["calendar_year"],
            "leave_type": "CASUAL",
            "total": total,
            "used": used,
            "remaining": total - used
        }

    finally:
        connection.close()


def _parse_date(value):
    try:
        return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError):
        return None


def _calculate_days(start_date, end_date):
    """
    Calculate calendar days inclusively.

    Example:
    Oct 6 to Oct 7 = 2 days.
    """

    return (end_date - start_date).days + 1


def check_leave_request(
    employee_id,
    leave_type,
    start_date,
    end_date
):
    """
    Validate a proposed leave request without creating it.
    """

    employee = get_employee_context(employee_id)

    if not employee["success"]:
        return employee

    start = _parse_date(start_date)
    end = _parse_date(end_date)

    if not start or not end:
        return {
            "success": False,
            "error": "Leave dates must use YYYY-MM-DD format."
        }

    if end < start:
        return {
            "success": False,
            "error": "End date cannot be before start date."
        }

    if start < date.today():
        return {
            "success": False,
            "error": "Leave cannot be requested for a date in the past."
        }

    leave_type = str(leave_type).strip().upper()

    if leave_type != "CASUAL":
        return {
            "success": False,
            "error": (
                "The current system supports CASUAL leave requests. "
                "Other leave types require HR policy configuration."
            )
        }

    days = _calculate_days(start, end)

    balance = get_leave_balance(employee_id, start.year)

    if not balance["success"]:
        return balance

    if balance["remaining"] < days:
        return {
            "success": False,
            "error": (
                f"Insufficient casual leave balance. "
                f"Available: {balance['remaining']} day(s), "
                f"requested: {days} day(s)."
            ),
            "balance": balance
        }

    connection = _connect()

    try:
        conflict = connection.execute(
            """
            SELECT request_id, status, start_date, end_date
            FROM leave_requests
            WHERE employee_id = ?
              AND status IN ('PENDING', 'APPROVED')
              AND start_date <= ?
              AND end_date >= ?
            """,
            (
                int(employee_id),
                end.isoformat(),
                start.isoformat()
            )
        ).fetchone()

        if conflict:
            return {
                "success": False,
                "error": (
                    f"Leave overlaps with existing request "
                    f"#{conflict['request_id']} "
                    f"({conflict['status']})."
                )
            }

        return {
            "success": True,
            "employee": employee,
            "leave_type": leave_type,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "days": days,
            "balance": balance
        }

    finally:
        connection.close()


def create_leave_request(
    employee_id,
    leave_type,
    start_date,
    end_date,
    reason=""
):
    """
    Create a real PENDING leave request.

    Important:
    This function performs the database transaction.
    The LLM must never directly manipulate leave balances.
    """

    validation = check_leave_request(
        employee_id,
        leave_type,
        start_date,
        end_date
    )

    if not validation["success"]:
        return validation

    employee = validation["employee"]
    days = validation["days"]

    manager_id = employee["manager_id"]

    if not manager_id:
        return {
            "success": False,
            "error": (
                "No reporting manager is configured for this employee. "
                "HR intervention is required."
            )
        }

    now = datetime.now().isoformat(timespec="seconds")

    connection = _connect()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO leave_requests
            (
                employee_id,
                leave_type,
                start_date,
                end_date,
                days,
                reason,
                status,
                manager_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?, ?, ?)
            """,
            (
                int(employee_id),
                validation["leave_type"],
                validation["start_date"],
                validation["end_date"],
                days,
                reason.strip() if reason else None,
                manager_id,
                now,
                now
            )
        )

        request_id = cursor.lastrowid

        _audit(
            connection,
            actor_id=employee_id,
            actor_name=employee["name"],
            action="LEAVE_REQUEST_CREATED",
            entity_type="LEAVE_REQUEST",
            entity_id=request_id,
            details=(
                f"{validation['leave_type']} leave request for "
                f"{validation['start_date']} to "
                f"{validation['end_date']} "
                f"({days} day(s))."
            )
        )

        connection.commit()

        return {
            "success": True,
            "request_id": request_id,
            "status": "PENDING",
            "employee_id": employee_id,
            "employee_name": employee["name"],
            "leave_type": validation["leave_type"],
            "start_date": validation["start_date"],
            "end_date": validation["end_date"],
            "days": days,
            "reason": reason.strip() if reason else "",
            "manager_id": manager_id,
            "manager_name": employee["manager_name"],
            "manager_email": employee["manager_email"],
            "remaining_balance": validation["balance"]["remaining"]
        }

    except sqlite3.Error as exc:
        connection.rollback()

        return {
            "success": False,
            "error": f"Unable to create leave request: {exc}"
        }

    finally:
        connection.close()


def get_leave_requests(employee_id=None, manager_id=None):
    """Retrieve leave requests for an employee or manager."""

    connection = _connect()

    try:
        if employee_id is not None:
            rows = connection.execute(
                """
                SELECT
                    lr.*,
                    e.name AS employee_name,
                    m.name AS manager_name
                FROM leave_requests lr
                JOIN employees e
                    ON lr.employee_id = e.employee_id
                JOIN employees m
                    ON lr.manager_id = m.employee_id
                WHERE lr.employee_id = ?
                ORDER BY lr.created_at DESC
                """,
                (int(employee_id),)
            ).fetchall()

        elif manager_id is not None:
            rows = connection.execute(
                """
                SELECT
                    lr.*,
                    e.name AS employee_name,
                    m.name AS manager_name
                FROM leave_requests lr
                JOIN employees e
                    ON lr.employee_id = e.employee_id
                JOIN employees m
                    ON lr.manager_id = m.employee_id
                WHERE lr.manager_id = ?
                ORDER BY lr.created_at DESC
                """,
                (int(manager_id),)
            ).fetchall()

        else:
            return {
                "success": False,
                "error": "employee_id or manager_id is required."
            }

        return {
            "success": True,
            "requests": [dict(row) for row in rows]
        }

    finally:
        connection.close()


def update_leave_request_status(
    request_id,
    manager_id,
    status,
    manager_comment=""
):
    """
    Approve or reject a pending leave request.

    Only the assigned reporting manager can perform this action.
    """

    status = str(status).strip().upper()

    if status not in {"APPROVED", "REJECTED"}:
        return {
            "success": False,
            "error": "Status must be APPROVED or REJECTED."
        }

    connection = _connect()

    try:
        request = connection.execute(
            """
            SELECT
                lr.*,
                e.name AS employee_name,
                m.name AS manager_name
            FROM leave_requests lr
            JOIN employees e
                ON lr.employee_id = e.employee_id
            JOIN employees m
                ON lr.manager_id = m.employee_id
            WHERE lr.request_id = ?
            """,
            (int(request_id),)
        ).fetchone()

        if request is None:
            return {
                "success": False,
                "error": f"Leave request #{request_id} was not found."
            }

        if request["manager_id"] != int(manager_id):
            return {
                "success": False,
                "error": "You are not authorized to process this request."
            }

        if request["status"] != "PENDING":
            return {
                "success": False,
                "error": (
                    f"Request #{request_id} is already "
                    f"{request['status']}."
                )
            }

        now = datetime.now().isoformat(timespec="seconds")

        # Re-check balance at approval time.
        # This prevents approval of a request after another
        # approved request consumed the available balance.
        if status == "APPROVED":

            balance = connection.execute(
                """
                SELECT
                    casual_leave_total,
                    casual_leave_used
                FROM leave_balances
                WHERE employee_id = ?
                  AND calendar_year = ?
                """,
                (
                    request["employee_id"],
                    date.fromisoformat(request["start_date"]).year
                )
            ).fetchone()

            if balance is None:
                return {
                    "success": False,
                    "error": "Leave balance could not be found."
                }

            remaining = (
                balance["casual_leave_total"]
                - balance["casual_leave_used"]
            )

            if remaining < request["days"]:
                return {
                    "success": False,
                    "error": (
                        "Cannot approve this request because the "
                        f"employee has only {remaining} day(s) remaining."
                    )
                }

            connection.execute(
                """
                UPDATE leave_balances
                SET
                    casual_leave_used = casual_leave_used + ?,
                    updated_at = ?
                WHERE employee_id = ?
                  AND calendar_year = ?
                """,
                (
                    request["days"],
                    now,
                    request["employee_id"],
                    date.fromisoformat(request["start_date"]).year
                )
            )

        connection.execute(
            """
            UPDATE leave_requests
            SET
                status = ?,
                manager_comment = ?,
                updated_at = ?,
                approved_at = ?
            WHERE request_id = ?
            """,
            (
                status,
                manager_comment.strip() if manager_comment else None,
                now,
                now if status == "APPROVED" else None,
                int(request_id)
            )
        )

        _audit(
            connection,
            actor_id=int(manager_id),
            actor_name=request["manager_name"],
            action=f"LEAVE_REQUEST_{status}",
            entity_type="LEAVE_REQUEST",
            entity_id=int(request_id),
            details=manager_comment.strip() if manager_comment else None
        )

        connection.commit()

        return {
            "success": True,
            "request_id": int(request_id),
            "status": status,
            "employee_id": request["employee_id"],
            "employee_name": request["employee_name"],
            "manager_name": request["manager_name"],
            "days": request["days"],
            "manager_comment": manager_comment.strip() if manager_comment else ""
        }

    except sqlite3.Error as exc:
        connection.rollback()

        return {
            "success": False,
            "error": f"Unable to update leave request: {exc}"
        }

    finally:
        connection.close()