from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.database.models import LeaveRequest
from app.database.repository import LeaveRepository


class LeaveAgent:
    """
    Specialized enterprise agent for leave management.

    Responsibilities:
    - Leave balance lookup
    - Leave history
    - Leave eligibility checks
    - Leave request creation
    - Leave request validation
    """

    name = "Leave Management Agent"

    description = (
        "Handles employee leave balances, leave history, "
        "eligibility checks and leave requests."
    )

    SUPPORTED_LEAVE_TYPES = {
        "casual": "Casual Leave",
        "sick": "Sick Leave",
        "vacation": "Vacation Leave",
        "earned": "Earned Leave",
    }

    def get_leave_balance(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        balance = LeaveRepository.get_balance(
            db,
            employee_id
        )

        if not balance:
            return {
                "success": False,
                "agent": self.name,
                "message": (
                    f"No leave balance was found for "
                    f"employee {employee_id}."
                )
            }

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "leave_balance": {
                column.name: getattr(balance, column.name)
                for column in balance.__table__.columns
                if column.name != "id"
            }
        }

    def get_leave_history(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        requests = LeaveRepository.get_requests(
            db,
            employee_id
        )

        history = []

        for request in requests:
            history.append({
                column.name: getattr(request, column.name)
                for column in request.__table__.columns
            })

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "count": len(history),
            "leave_history": history
        }

    def check_eligibility(
        self,
        db: Session,
        employee_id: int,
        leave_type: str,
        start_date: date,
        end_date: date
    ) -> dict:

        if end_date < start_date:
            return {
                "success": False,
                "eligible": False,
                "agent": self.name,
                "message": "End date cannot be before start date."
            }

        normalized_type = leave_type.lower().strip()

        if normalized_type not in self.SUPPORTED_LEAVE_TYPES:
            return {
                "success": False,
                "eligible": False,
                "agent": self.name,
                "message": (
                    f"Unsupported leave type: {leave_type}. "
                    f"Supported types are: "
                    f"{', '.join(self.SUPPORTED_LEAVE_TYPES.values())}."
                )
            }

        balance = LeaveRepository.get_balance(
            db,
            employee_id
        )

        if not balance:
            return {
                "success": False,
                "eligible": False,
                "agent": self.name,
                "message": "Leave balance could not be found."
            }

        requested_days = (
            end_date - start_date
        ).days + 1

        balance_column_map = {
            "casual": "casual_leave",
            "sick": "sick_leave",
            "vacation": "earned_leave",
            "earned": "earned_leave",
        }

        column_name = balance_column_map.get(
            normalized_type
        )

        available_days = getattr(
            balance,
            column_name,
            0
        )

        if requested_days > available_days:
            return {
                "success": True,
                "eligible": False,
                "agent": self.name,
                "message": (
                    f"Insufficient {self.SUPPORTED_LEAVE_TYPES[normalized_type]} "
                    f"balance. Requested {requested_days} day(s), "
                    f"but only {available_days} day(s) are available."
                ),
                "requested_days": requested_days,
                "available_days": available_days,
            }

        return {
            "success": True,
            "eligible": True,
            "agent": self.name,
            "message": (
                f"Employee is eligible for "
                f"{requested_days} day(s) of "
                f"{self.SUPPORTED_LEAVE_TYPES[normalized_type]}."
            ),
            "requested_days": requested_days,
            "available_days": available_days,
        }

    def apply_leave(
        self,
        db: Session,
        employee_id: int,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: str = ""
    ) -> dict:

        eligibility = self.check_eligibility(
            db=db,
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date
        )

        if not eligibility.get("eligible"):
            return eligibility

        normalized_type = leave_type.lower().strip()

        request = LeaveRequest(
            employee_id=employee_id,
            leave_type=self.SUPPORTED_LEAVE_TYPES[
                normalized_type
            ],
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="Pending",
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        return {
            "success": True,
            "agent": self.name,
            "message": (
                "Leave request submitted successfully "
                "and is awaiting approval."
            ),
            "request_id": request.id,
            "employee_id": employee_id,
            "leave_type": self.SUPPORTED_LEAVE_TYPES[
                normalized_type
            ],
            "start_date": str(start_date),
            "end_date": str(end_date),
            "status": "Pending",
        }


leave_agent = LeaveAgent()