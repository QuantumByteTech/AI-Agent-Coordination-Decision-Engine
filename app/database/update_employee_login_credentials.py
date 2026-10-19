
"""Preview or create missing employee login accounts.

Username: first.last.employeecode
Password: initials@employee-code-number

Default: preview only.
Use --apply to create missing accounts and update credentials
for existing linked EMPLOYEE accounts.

HR and unlinked user accounts are preserved.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from app.auth.auth_service import hash_password
from app.database.database import SessionLocal
from app.database.models import Employee, User


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", ".", value)
    return value.strip(".")


def make_credentials(employee: Employee) -> tuple[str, str]:
    first = (employee.first_name or "").strip()
    last = (employee.last_name or "").strip()
    code = (employee.employee_code or "").strip()

    initials = "".join(part[0] for part in (first, last) if part)
    digits = "".join(re.findall(r"\d", code))

    if not first or not last or not initials or not digits or not code:
        raise ValueError(
            f"Employee id={employee.id} has incomplete name/code data."
        )

    username = f"{slug(first)}.{slug(last)}.{slug(code)}"
    password = f"{initials.upper()}@{digits}"
    return username, password


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="create missing accounts and update existing linked employee credentials",
    )
    args = parser.parse_args()

    db = SessionLocal()

    try:
        employees = db.query(Employee).order_by(Employee.id).all()

        # Keep every existing account intact unless it is linked to an employee.
        all_users = db.query(User).order_by(User.id).all()
        users_by_employee = {}

        for user in all_users:
            if user.employee_id is not None:
                users_by_employee.setdefault(user.employee_id, []).append(user)

        existing_usernames = {
            user.username.casefold()
            for user in all_users
            if user.username
        }

        planned = []
        seen_usernames = set()

        for employee in employees:
            username, password = make_credentials(employee)
            key = username.casefold()

            if key in seen_usernames:
                raise ValueError(
                    f"Duplicate generated username {username!r}; no changes made."
                )
            seen_usernames.add(key)

            linked = users_by_employee.get(employee.id, [])

            if len(linked) > 1:
                raise ValueError(
                    f"Employee id={employee.id} has multiple linked accounts; "
                    "resolve this before continuing."
                )

            if linked:
                user = linked[0]

                if (user.role or "").upper() != "EMPLOYEE":
                    raise ValueError(
                        f"Employee id={employee.id} is linked to non-EMPLOYEE "
                        f"account id={user.id}; no changes made."
                    )

                # Existing linked employee accounts will be updated on --apply.
                if key in existing_usernames and user.username.casefold() != key:
                    raise ValueError(
                        f"Username {username!r} is already taken; no changes made."
                    )

                planned.append(
                    ("UPDATE", user, employee, username, password)
                )
            else:
                # Do not overwrite or reuse any existing account name.
                if key in existing_usernames:
                    raise ValueError(
                        f"Username {username!r} is already taken by another "
                        "account; no changes made."
                    )

                planned.append(
                    ("CREATE", None, employee, username, password)
                )

            existing_usernames.add(key)

        mode = "APPLY MODE" if args.apply else "PREVIEW ONLY"
        print(f"{mode} — " + (
            "database changes are planned."
            if args.apply else "database is unchanged."
        ))
        print(f"Employees found: {len(employees)}")
        print(f"Accounts to create: {sum(p[0] == 'CREATE' for p in planned)}")
        print(f"Accounts to update: {sum(p[0] == 'UPDATE' for p in planned)}")
        print("\nCredential format: username = first.last.code")
        print("Password format: initials@numeric-code\n")

        for action, _user, employee, username, password in planned:
            print(
                f"{action}: {employee.first_name} {employee.last_name} "
                f"({employee.employee_code}) -> {username} | {password}"
            )

        if not args.apply:
            print("\nNo database changes were made.")
            print("Back up the database, review this preview, then use --apply.")
            return 0

        # Build a credentials export only after all checks have passed.
        export_rows = []

        for action, user, employee, username, password in planned:
            if action == "CREATE":
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role="EMPLOYEE",
                    employee_id=employee.id,
                    is_active=True,
                )
                db.add(user)
            else:
                user.username = username
                user.password_hash = hash_password(password)
                user.is_active = True

            export_rows.append({
                "employee_code": employee.employee_code,
                "employee_name": (
                    f"{employee.first_name} {employee.last_name}"
                ),
                "username": username,
                "temporary_demo_password": password,
            })

        db.commit()

        export_path = Path("data/employee_demo_credentials.csv")
        export_path.parent.mkdir(parents=True, exist_ok=True)

        with export_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "employee_code",
                    "employee_name",
                    "username",
                    "temporary_demo_password",
                ],
            )
            writer.writeheader()
            writer.writerows(export_rows)

        print(f"\nCreated/updated {len(export_rows)} employee accounts.")
        print(f"Credentials exported to: {export_path}")
        print("HR and unlinked user accounts were not modified.")
        print(
            "WARNING: These predictable passwords are for a controlled demo "
            "only, not real deployment."
        )
        return 0

    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}\nNo database changes were committed.", file=sys.stderr)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
