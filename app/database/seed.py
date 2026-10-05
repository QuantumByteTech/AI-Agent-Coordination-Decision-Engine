from datetime import date, datetime, timedelta
import random

from app.database.database import Base, SessionLocal, engine
from app.database.models import (
    AgentActivityLog,
    Attendance,
    Department,
    Designation,
    Employee,
    HRPolicy,
    HRRequest,
    LeaveBalance,
    LeaveRequest,
    OffboardingRecord,
    OnboardingRecord,
    WorkflowExecution,
)


random.seed(42)


# =========================================================
# COMPANY CONFIGURATION
# =========================================================

COMPANY_NAME = "NexaCore Technologies"

DEPARTMENTS = [
    ("Engineering", "Bengaluru"),
    ("Data & AI", "Bengaluru"),
    ("Human Resources", "Pune"),
    ("Finance", "Mumbai"),
    ("Sales", "Mumbai"),
    ("Marketing", "Pune"),
    ("Operations", "Hyderabad"),
    ("Information Technology", "Bengaluru"),
    ("Cybersecurity", "Hyderabad"),
    ("Customer Success", "Pune"),
]

DESIGNATIONS = [
    ("Chief Technology Officer", "Executive"),
    ("Engineering Manager", "Manager"),
    ("Senior Software Engineer", "Senior"),
    ("Software Engineer", "Mid"),
    ("Associate Software Engineer", "Junior"),
    ("Data Scientist", "Senior"),
    ("Data Analyst", "Mid"),
    ("AI Engineer", "Mid"),
    ("HR Manager", "Manager"),
    ("HR Executive", "Mid"),
    ("Finance Manager", "Manager"),
    ("Financial Analyst", "Mid"),
    ("Sales Manager", "Manager"),
    ("Sales Executive", "Mid"),
    ("Marketing Manager", "Manager"),
    ("Marketing Executive", "Mid"),
    ("Operations Manager", "Manager"),
    ("Operations Executive", "Mid"),
    ("IT Manager", "Manager"),
    ("IT Support Engineer", "Mid"),
    ("Cybersecurity Analyst", "Mid"),
    ("Security Engineer", "Senior"),
    ("Customer Success Manager", "Manager"),
    ("Customer Success Executive", "Mid"),
]

FIRST_NAMES = [
    "Aarav", "Aditya", "Aisha", "Akash", "Ananya",
    "Arjun", "Diya", "Ishaan", "Kabir", "Kavya",
    "Meera", "Nisha", "Neha", "Rahul", "Riya",
    "Rohan", "Saanvi", "Sahil", "Simran", "Tanvi",
    "Varun", "Vikram", "Yash", "Zoya", "Aditi",
    "Aman", "Dev", "Ira", "Karan", "Maya",
]

LAST_NAMES = [
    "Sharma", "Patel", "Mehta", "Joshi", "Kulkarni",
    "Deshmukh", "Nair", "Iyer", "Rao", "Khan",
    "Shah", "Gupta", "Singh", "Verma", "Kapoor",
    "Malhotra", "Bose", "Chopra", "Pillai", "Menon",
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def random_date(start_year=2020, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 10, 1)

    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def random_birth_date():
    today = date(2026, 10, 5)

    age = random.randint(21, 58)

    year = today.year - age

    month = random.randint(1, 12)

    if month == 2:
        day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 28)

    return date(year, month, day)


def random_phone():
    return "9" + "".join(
        str(random.randint(0, 9))
        for _ in range(9)
    )


def employee_email(first_name, last_name, employee_number):
    return (
        f"{first_name.lower()}."
        f"{last_name.lower()}"
        f"{employee_number}@nexacore.example"
    )


# =========================================================
# CREATE DATABASE
# =========================================================

def reset_database():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Database tables recreated.")


# =========================================================
# DEPARTMENTS
# =========================================================

def create_departments(db):

    departments = []

    for name, location in DEPARTMENTS:

        department = Department(
            name=name,
            location=location,
        )

        db.add(department)
        departments.append(department)

    db.flush()

    return departments


# =========================================================
# DESIGNATIONS
# =========================================================

def create_designations(db):

    designations = []

    for title, level in DESIGNATIONS:

        designation = Designation(
            title=title,
            level=level,
        )

        db.add(designation)
        designations.append(designation)

    db.flush()

    return designations


# =========================================================
# EMPLOYEES
# =========================================================

def create_employees(db, departments, designations):

    employees = []

    used_names = set()

    for number in range(1, 201):

        while True:

            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            name_key = (
                first_name,
                last_name,
                number
            )

            if name_key not in used_names:
                used_names.add(name_key)
                break

        department = random.choice(departments)

        department_designations = [
            d for d in designations
            if (
                d.title.startswith("Engineering")
                or d.title.startswith("Software")
                or d.title.startswith("Associate Software")
                or d.title.startswith("Data")
                or d.title.startswith("AI")
                or d.title.startswith("HR")
                or d.title.startswith("Finance")
                or d.title.startswith("Sales")
                or d.title.startswith("Marketing")
                or d.title.startswith("Operations")
                or d.title.startswith("IT")
                or d.title.startswith("Cybersecurity")
                or d.title.startswith("Security")
                or d.title.startswith("Customer")
            )
        ]

        designation = random.choice(department_designations)

        joining_date = random_date(2020, 2026)

        employee = Employee(
            employee_code=f"NXT{1000 + number}",
            first_name=first_name,
            last_name=last_name,
            email=employee_email(
                first_name,
                last_name,
                number,
            ),
            phone=random_phone(),
            date_of_birth=random_birth_date(),
            joining_date=joining_date,
            department_id=department.id,
            designation_id=designation.id,
            employment_type=random.choice(
                [
                    "Full-Time",
                    "Full-Time",
                    "Full-Time",
                    "Contract",
                    "Intern",
                ]
            ),
            employment_status=random.choices(
                [
                    "Active",
                    "Active",
                    "Active",
                    "On Leave",
                    "Resigned",
                ],
                weights=[70, 10, 8, 7, 5],
            )[0],
            salary=random.randint(
                450000,
                2800000
            ),
        )

        db.add(employee)
        employees.append(employee)

    db.flush()

    return employees


# =========================================================
# MANAGERS
# =========================================================

def assign_managers(db, employees):

    managers = [
        employee
        for employee in employees
        if employee.designation_id % 5 == 0
    ]

    if not managers:
        return

    for employee in employees:

        if employee in managers:
            continue

        manager = random.choice(managers)

        if manager.id != employee.id:
            employee.manager_id = manager.id


# =========================================================
# LEAVE BALANCES
# =========================================================

def create_leave_balances(db, employees):

    for employee in employees:

        balance = LeaveBalance(
            employee_id=employee.id,
            casual_leave=random.randint(3, 12),
            sick_leave=random.randint(3, 10),
            earned_leave=random.randint(5, 18),
        )

        db.add(balance)


# =========================================================
# LEAVE REQUESTS
# =========================================================

def create_leave_requests(db, employees):

    leave_types = [
        "Casual Leave",
        "Sick Leave",
        "Earned Leave",
        "Vacation Leave",
    ]

    statuses = [
        "Approved",
        "Approved",
        "Approved",
        "Pending",
        "Rejected",
    ]

    reasons = [
        "Personal work",
        "Family function",
        "Medical appointment",
        "Health reasons",
        "Vacation",
        "Personal emergency",
        "Family emergency",
    ]

    for _ in range(500):

        employee = random.choice(employees)

        start_date = random_date(2024, 2026)

        duration = random.randint(1, 5)

        end_date = start_date + timedelta(
            days=duration - 1
        )

        request = LeaveRequest(
            employee_id=employee.id,
            leave_type=random.choice(leave_types),
            start_date=start_date,
            end_date=end_date,
            reason=random.choice(reasons),
            status=random.choice(statuses),
            requested_at=datetime.combine(
                start_date,
                datetime.min.time()
            ),
        )

        db.add(request)


# =========================================================
# ATTENDANCE
# =========================================================

def create_attendance(db, employees):

    today = date(2026, 10, 5)

    for employee in employees:

        for days_back in range(30):

            attendance_date = today - timedelta(
                days=days_back
            )

            status = random.choices(
                [
                    "Present",
                    "Present",
                    "Present",
                    "Work From Home",
                    "Absent",
                    "Leave",
                ],
                weights=[
                    55,
                    15,
                    10,
                    10,
                    5,
                    5,
                ],
            )[0]

            if status in ["Present", "Work From Home"]:

                check_in = random.choice(
                    [
                        "08:45",
                        "09:00",
                        "09:15",
                        "09:30",
                        "09:45",
                    ]
                )

                check_out = random.choice(
                    [
                        "17:30",
                        "18:00",
                        "18:15",
                        "18:30",
                        "19:00",
                    ]
                )

            else:

                check_in = None
                check_out = None

            attendance = Attendance(
                employee_id=employee.id,
                attendance_date=attendance_date,
                status=status,
                check_in=check_in,
                check_out=check_out,
            )

            db.add(attendance)


# =========================================================
# HR REQUESTS
# =========================================================

def create_hr_requests(db, employees):

    request_types = [
        "Leave Query",
        "Attendance Issue",
        "Payroll Query",
        "Work From Home Request",
        "Employee Information",
        "Policy Question",
        "Benefits Query",
        "Onboarding Support",
        "IT Access Request",
    ]

    descriptions = [
        "Employee requested clarification regarding company policy.",
        "Employee reported an attendance discrepancy.",
        "Employee requested information about available benefits.",
        "Employee requested work-from-home approval.",
        "Employee requested assistance with an HR process.",
    ]

    for _ in range(300):

        request = HRRequest(
            employee_id=random.choice(employees).id,
            request_type=random.choice(request_types),
            description=random.choice(descriptions),
            priority=random.choice(
                [
                    "Low",
                    "Medium",
                    "Medium",
                    "High",
                ]
            ),
            status=random.choice(
                [
                    "Open",
                    "In Progress",
                    "Resolved",
                    "Pending",
                ]
            ),
        )

        db.add(request)


# =========================================================
# POLICIES
# =========================================================

def create_policies(db):

    policies = [
        (
            "Casual Leave Policy",
            "Leave",
            "Employees are eligible for casual leave according to their employment policy."
        ),
        (
            "Sick Leave Policy",
            "Leave",
            "Employees should notify their manager as soon as possible when taking sick leave."
        ),
        (
            "Work From Home Policy",
            "Attendance",
            "Eligible employees may work remotely subject to manager approval and business requirements."
        ),
        (
            "Working Hours Policy",
            "Attendance",
            "Standard working hours are 9:00 AM to 6:00 PM with applicable breaks."
        ),
        (
            "Attendance Policy",
            "Attendance",
            "Employees are expected to maintain accurate attendance records."
        ),
        (
            "Parental Leave Policy",
            "Benefits",
            "Eligible employees may apply for parental leave according to company guidelines."
        ),
        (
            "Employee Conduct Policy",
            "Company Rules",
            "Employees are expected to maintain professional conduct in the workplace."
        ),
        (
            "Information Security Policy",
            "Security",
            "Employees must protect company information and follow security procedures."
        ),
        (
            "Remote Access Policy",
            "Security",
            "Remote access to enterprise systems must use approved authentication mechanisms."
        ),
        (
            "Onboarding Policy",
            "Employee Lifecycle",
            "New employees must complete documentation, equipment allocation, and orientation."
        ),
    ]

    for name, category, description in policies:

        db.add(
            HRPolicy(
                policy_name=name,
                category=category,
                description=description,
                active=True,
            )
        )


# =========================================================
# ONBOARDING
# =========================================================

def create_onboarding_records(db, employees):

    recent_employees = [
        employee
        for employee in employees
        if employee.joining_date >= date(2025, 1, 1)
    ]

    for employee in recent_employees[:60]:

        db.add(
            OnboardingRecord(
                employee_id=employee.id,
                joining_date=employee.joining_date,
                documentation_status=random.choice(
                    [
                        "Completed",
                        "Completed",
                        "Pending",
                    ]
                ),
                equipment_status=random.choice(
                    [
                        "Completed",
                        "Pending",
                    ]
                ),
                orientation_status=random.choice(
                    [
                        "Completed",
                        "Pending",
                    ]
                ),
                overall_status=random.choice(
                    [
                        "Completed",
                        "In Progress",
                        "Pending",
                    ]
                ),
            )
        )


# =========================================================
# OFFBOARDING
# =========================================================

def create_offboarding_records(db, employees):

    resigned_employees = [
        employee
        for employee in employees
        if employee.employment_status == "Resigned"
    ]

    for employee in resigned_employees:

        resignation_date = date(
            2026,
            random.randint(1, 9),
            random.randint(1, 25),
        )

        last_working_date = resignation_date + timedelta(
            days=random.randint(15, 60)
        )

        db.add(
            OffboardingRecord(
                employee_id=employee.id,
                resignation_date=resignation_date,
                last_working_date=last_working_date,
                exit_interview_status=random.choice(
                    [
                        "Completed",
                        "Pending",
                    ]
                ),
                asset_return_status=random.choice(
                    [
                        "Completed",
                        "Pending",
                    ]
                ),
                clearance_status=random.choice(
                    [
                        "Completed",
                        "Pending",
                    ]
                ),
                overall_status=random.choice(
                    [
                        "Completed",
                        "In Progress",
                    ]
                ),
            )
        )


# =========================================================
# SAMPLE WORKFLOW EXECUTIONS
# =========================================================

def create_workflow_data(db, employees):

    workflow_types = [
        "Leave Approval",
        "Employee Information",
        "Policy Query",
        "Attendance Analysis",
        "Onboarding",
        "Offboarding",
        "HR Request Resolution",
    ]

    for _ in range(100):

        employee = random.choice(employees)

        workflow = WorkflowExecution(
            employee_id=employee.id,
            workflow_type=random.choice(workflow_types),
            status=random.choice(
                [
                    "Completed",
                    "Completed",
                    "In Progress",
                    "Pending",
                ]
            ),
            decision=random.choice(
                [
                    "Approved",
                    "Recommended for approval",
                    "Requires HR review",
                    "Information retrieved",
                    "No action required",
                ]
            ),
        )

        db.add(workflow)

    db.flush()


# =========================================================
# MAIN SEED PROCESS
# =========================================================

def seed_database():

    reset_database()

    db = SessionLocal()

    try:

        departments = create_departments(db)

        designations = create_designations(db)

        employees = create_employees(
            db,
            departments,
            designations,
        )

        assign_managers(
            db,
            employees,
        )

        create_leave_balances(
            db,
            employees,
        )

        create_leave_requests(
            db,
            employees,
        )

        create_attendance(
            db,
            employees,
        )

        create_hr_requests(
            db,
            employees,
        )

        create_policies(
            db,
        )

        create_onboarding_records(
            db,
            employees,
        )

        create_offboarding_records(
            db,
            employees,
        )

        create_workflow_data(
            db,
            employees,
        )

        db.commit()

        print()
        print("=" * 60)
        print("NexaCore Technologies database seeded successfully.")
        print("=" * 60)
        print(f"Employees created: {len(employees)}")
        print("Leave requests: 500")
        print("Attendance records: 6000")
        print("HR requests: 300")
        print("HR policies: 10")
        print("Workflow records: 100")
        print("=" * 60)

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_database()