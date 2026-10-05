from sqlalchemy.orm import Session

from app.database.repository import AttendanceRepository


class AttendanceAgent:
    """
    Specialized agent responsible for employee attendance
    information and attendance analysis.
    """

    name = "Attendance Intelligence Agent"

    description = (
        "Retrieves attendance records and generates "
        "attendance summaries for HR workflows."
    )

    def get_employee_attendance(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        records = AttendanceRepository.get_employee_attendance(
            db,
            employee_id
        )

        attendance = []

        for record in records:
            attendance.append({
                column.name: getattr(record, column.name)
                for column in record.__table__.columns
            })

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "count": len(attendance),
            "attendance": attendance
        }

    def get_attendance_summary(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        records = AttendanceRepository.get_employee_attendance(
            db,
            employee_id
        )

        if not records:
            return {
                "success": False,
                "agent": self.name,
                "employee_id": employee_id,
                "message": "No attendance records were found."
            }

        summary = {
            "total_records": len(records),
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0
        }

        for record in records:
            status = str(
                getattr(record, "status", "")
            ).lower()

            if status == "present":
                summary["present"] += 1
            elif status == "absent":
                summary["absent"] += 1
            elif status == "late":
                summary["late"] += 1
            elif status == "leave":
                summary["leave"] += 1

        total = summary["total_records"]

        summary["attendance_percentage"] = round(
            (summary["present"] / total) * 100,
            2
        )

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "summary": summary
        }

    def get_all_attendance(
        self,
        db: Session
    ) -> dict:

        records = AttendanceRepository.get_all_attendance(db)

        attendance = []

        for record in records:
            attendance.append({
                column.name: getattr(record, column.name)
                for column in record.__table__.columns
            })

        return {
            "success": True,
            "agent": self.name,
            "count": len(attendance),
            "attendance": attendance
        }


attendance_agent = AttendanceAgent()