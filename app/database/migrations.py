import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "hr_enterprise.db"
)


def migrate_department_headcount() -> None:
    """Add target_headcount if missing, preserving existing records."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(departments)"
            ).fetchall()
        }

        if not columns:
            raise RuntimeError(
                "The departments table was not found. "
                "Migration cancelled."
            )

        if "target_headcount" not in columns:
            connection.execute(
                """
                ALTER TABLE departments
                ADD COLUMN target_headcount INTEGER NOT NULL DEFAULT 0
                """
            )
            connection.commit()
            print("Migration complete: target_headcount added.")
        else:
            print("Migration skipped: target_headcount already exists.")

    finally:
        connection.close()


if __name__ == "__main__":
    migrate_department_headcount()