from sqlalchemy.orm import Session

from app.database.repository import (
    OnboardingRepository,
    OffboardingRepository,
)


class LifecycleAgent:
    """
    Specialized HR agent responsible for employee lifecycle
    operations including onboarding and offboarding.
    """

    name = "Employee Lifecycle Agent"

    description = (
        "Handles employee onboarding and offboarding information "
        "through the enterprise HR database."
    )

    def get_onboarding(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        record = OnboardingRepository.get_by_employee(
            db,
            employee_id
        )

        if not record:
            return {
                "success": False,
                "agent": self.name,
                "employee_id": employee_id,
                "message": (
                    "No onboarding record was found for "
                    f"employee {employee_id}."
                )
            }

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "type": "ONBOARDING",
            "record": {
                column.name: getattr(record, column.name)
                for column in record.__table__.columns
            }
        }

    def get_offboarding(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        record = OffboardingRepository.get_by_employee(
            db,
            employee_id
        )

        if not record:
            return {
                "success": False,
                "agent": self.name,
                "employee_id": employee_id,
                "message": (
                    "No offboarding record was found for "
                    f"employee {employee_id}."
                )
            }

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "type": "OFFBOARDING",
            "record": {
                column.name: getattr(record, column.name)
                for column in record.__table__.columns
            }
        }

    def get_employee_lifecycle(
        self,
        db: Session,
        employee_id: int
    ) -> dict:

        onboarding = OnboardingRepository.get_by_employee(
            db,
            employee_id
        )

        offboarding = OffboardingRepository.get_by_employee(
            db,
            employee_id
        )

        return {
            "success": True,
            "agent": self.name,
            "employee_id": employee_id,
            "onboarding": (
                {
                    column.name: getattr(onboarding, column.name)
                    for column in onboarding.__table__.columns
                }
                if onboarding
                else None
            ),
            "offboarding": (
                {
                    column.name: getattr(offboarding, column.name)
                    for column in offboarding.__table__.columns
                }
                if offboarding
                else None
            )
        }


lifecycle_agent = LifecycleAgent()