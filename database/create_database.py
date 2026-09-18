import sqlite3
from pathlib import Path


# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database location
DB_PATH = BASE_DIR / "database" / "employees.db"


def create_database():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Create employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            joining_date TEXT NOT NULL
        )
    """)

    # Demo employee records
    employees = [
        (
            1,
            "James Anderson",
            "Engineering",
            "Software Engineer",
            "james.anderson@worksphere.com",
            "2025-07-15"
        ),

        (
            2,
            "Emma Williams",
            "Human Resources",
            "HR Executive",
            "emma.williams@worksphere.com",
            "2024-11-04"
        ),

        (
            3,
            "Oliver Bennett",
            "Finance",
            "Financial Analyst",
            "oliver.bennett@worksphere.com",
            "2025-02-10"
        ),

        (
            4,
            "Sophia Mitchell",
            "Engineering",
            "Senior Software Engineer",
            "sophia.mitchell@worksphere.com",
            "2023-08-21"
        ),

        (
            5,
            "Daniel Carter",
            "Operations",
            "Operations Manager",
            "daniel.carter@worksphere.com",
            "2022-05-16"
        ),

        (
            6,
            "Amelia Thompson",
            "Marketing",
            "Marketing Specialist",
            "amelia.thompson@worksphere.com",
            "2025-01-06"
        ),

        (
            7,
            "William Parker",
            "Engineering",
            "Backend Developer",
            "william.parker@worksphere.com",
            "2024-06-24"
        ),

        (
            8,
            "Charlotte Morgan",
            "Human Resources",
            "HR Manager",
            "charlotte.morgan@worksphere.com",
            "2021-09-13"
        )
    ]

    # Insert employees
    cursor.executemany("""
        INSERT OR IGNORE INTO employees
        (
            employee_id,
            name,
            department,
            designation,
            email,
            joining_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, employees)

    connection.commit()
    connection.close()

    print("Employee database created successfully.")
    print(f"Database location: {DB_PATH}")
    print(f"Employees added: {len(employees)}")


if __name__ == "__main__":
    create_database()