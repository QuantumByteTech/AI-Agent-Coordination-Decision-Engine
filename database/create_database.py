import sqlite3
from pathlib import Path
from datetime import datetime


# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database location
DB_PATH = BASE_DIR / "database" / "employees.db"


EMPLOYEES = [
    (
        1,
        "James Anderson",
        "Engineering",
        "Software Engineer",
        "james.anderson@worksphere.com",
        "2025-07-15",
        4,
    ),
    (
        2,
        "Emma Williams",
        "Human Resources",
        "HR Executive",
        "emma.williams@worksphere.com",
        "2024-11-04",
        8,
    ),
    (
        3,
        "Oliver Bennett",
        "Finance",
        "Financial Analyst",
        "oliver.bennett@worksphere.com",
        "2025-02-10",
        5,
    ),
    (
        4,
        "Sophia Mitchell",
        "Engineering",
        "Senior Software Engineer",
        "sophia.mitchell@worksphere.com",
        "2023-08-21",
        8,
    ),
    (
        5,
        "Daniel Carter",
        "Operations",
        "Operations Manager",
        "daniel.carter@worksphere.com",
        "2022-05-16",
        8,
    ),
    (
        6,
        "Amelia Thompson",
        "Marketing",
        "Marketing Specialist",
        "amelia.thompson@worksphere.com",
        "2025-01-06",
        5,
    ),
    (
        7,
        "William Parker",
        "Engineering",
        "Backend Developer",
        "william.parker@worksphere.com",
        "2024-06-24",
        4,
    ),
    (
        8,
        "Charlotte Morgan",
        "Human Resources",
        "HR Manager",
        "charlotte.morgan@worksphere.com",
        "2021-09-13",
        None,
    ),
]


def create_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # 1. Employees
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            joining_date TEXT NOT NULL,
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
        )
    """)

    # Existing databases do not have manager_id.
    columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(employees)").fetchall()
    }

    if "manager_id" not in columns:
        cursor.execute("""
            ALTER TABLE employees
            ADD COLUMN manager_id INTEGER
        """)

    # Insert existing employees without overwriting records.
    cursor.executemany("""
        INSERT OR IGNORE INTO employees
        (
            employee_id,
            name,
            department,
            designation,
            email,
            joining_date,
            manager_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, EMPLOYEES)

    # Update manager relationships.
    for employee in EMPLOYEES:
        cursor.execute("""
            UPDATE employees
            SET manager_id = ?
            WHERE employee_id = ?
        """, (employee[6], employee[0]))

    # ---------------------------------------------------------
    # 2. Leave balances
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_balances (
            balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            calendar_year INTEGER NOT NULL,
            casual_leave_total INTEGER NOT NULL DEFAULT 12,
            casual_leave_used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(employee_id, calendar_year),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    """)

    current_year = datetime.now().year
    now = datetime.now().isoformat(timespec="seconds")

    employee_ids = [
        row[0]
        for row in cursor.execute(
            "SELECT employee_id FROM employees"
        ).fetchall()
    ]

    for employee_id in employee_ids:
        cursor.execute("""
            INSERT OR IGNORE INTO leave_balances
            (
                employee_id,
                calendar_year,
                casual_leave_total,
                casual_leave_used,
                created_at,
                updated_at
            )
            VALUES (?, ?, 12, 0, ?, ?)
        """, (employee_id, current_year, now, now))

    # ---------------------------------------------------------
    # 3. Leave requests
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            reason TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING',
            manager_id INTEGER NOT NULL,
            manager_comment TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            approved_at TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
        )
    """)

    # ---------------------------------------------------------
    # 4. Audit logs
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id INTEGER,
            actor_name TEXT,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            details TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (actor_id) REFERENCES employees(employee_id)
        )
    """)

    # ---------------------------------------------------------
    # 5. Indexes
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_leave_requests_employee
        ON leave_requests(employee_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_leave_requests_manager
        ON leave_requests(manager_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_leave_requests_status
        ON leave_requests(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
        ON audit_logs(entity_type, entity_id)
    """)

    connection.commit()

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------
    employee_count = cursor.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    balance_count = cursor.execute(
        "SELECT COUNT(*) FROM leave_balances"
    ).fetchone()[0]

    connection.close()

    print("Enterprise HR database initialized successfully.")
    print(f"Database: {DB_PATH}")
    print(f"Employees: {employee_count}")
    print(f"Leave balances: {balance_count}")
    print("Tables:")
    print("  - employees")
    print("  - leave_balances")
    print("  - leave_requests")
    print("  - audit_logs")


if __name__ == "__main__":
    create_database()